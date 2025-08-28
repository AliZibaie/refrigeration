from django.shortcuts import render
from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy
from .models import Calculation, Refrigerant, StatePoint
from .diagrams import ThermodynamicDiagrams
import CoolProp.CoolProp as CP


class CalculationCreateView(CreateView):
    model = Calculation
    fields = ['cycle_type', 'refrigerant', 'expansion_device', 'evaporator_temp', 'condenser_temp', 'generator_temp',
              'absorber_temp']
    template_name = 'cycle_calculator/calculate.html'
    success_url = reverse_lazy('calculation_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.perform_calculation(self.object)
        return response

    def perform_calculation(self, calculation):
        try:
            refrigerant = calculation.refrigerant.coolprop_name

            if calculation.cycle_type == 'vapor_compression':
                self.calculate_vapor_compression(calculation, refrigerant)
            elif calculation.cycle_type == 'absorption':
                self.calculate_absorption(calculation, refrigerant)

        except Exception as e:
            print(f"Calculation error: {e}")

    def calculate_vapor_compression(self, calc, refrigerant):
        T_evap = calc.evaporator_temp + 273.15
        T_cond = calc.condenser_temp + 273.15

        # State points
        P_low = CP.PropsSI('P', 'T', T_evap, 'Q', 1, refrigerant)
        P_high = CP.PropsSI('P', 'T', T_cond, 'Q', 0, refrigerant)

        # Point 1: Evaporator exit (saturated vapor)
        h1 = CP.PropsSI('H', 'T', T_evap, 'Q', 1, refrigerant)
        s1 = CP.PropsSI('S', 'T', T_evap, 'Q', 1, refrigerant)

        StatePoint.objects.create(
            calculation=calc, point_number=1,
            temperature=T_evap - 273.15, pressure=P_low / 1000,
            enthalpy=h1 / 1000, entropy=s1 / 1000, quality=1.0
        )

        # Point 2: Compressor exit
        s2 = s1  # Isentropic compression
        h2 = CP.PropsSI('H', 'P', P_high, 'S', s2, refrigerant)
        T2 = CP.PropsSI('T', 'P', P_high, 'H', h2, refrigerant)

        StatePoint.objects.create(
            calculation=calc, point_number=2,
            temperature=T2 - 273.15, pressure=P_high / 1000,
            enthalpy=h2 / 1000, entropy=s2 / 1000
        )

        # Point 3: Condenser exit (saturated liquid)
        h3 = CP.PropsSI('H', 'T', T_cond, 'Q', 0, refrigerant)
        s3 = CP.PropsSI('S', 'T', T_cond, 'Q', 0, refrigerant)

        StatePoint.objects.create(
            calculation=calc, point_number=3,
            temperature=T_cond - 273.15, pressure=P_high / 1000,
            enthalpy=h3 / 1000, entropy=s3 / 1000, quality=0.0
        )

        # Point 4: After expansion
        if calc.expansion_device == 'throttle':
            # Throttling: h4 = h3
            h4 = h3
            T4 = CP.PropsSI('T', 'P', P_low, 'H', h4, refrigerant)
            s4 = CP.PropsSI('S', 'P', P_low, 'H', h4, refrigerant)
            x4 = CP.PropsSI('Q', 'P', P_low, 'H', h4, refrigerant)
        else:
            # Turbine: s4 = s3 (isentropic)
            s4 = s3
            h4 = CP.PropsSI('H', 'P', P_low, 'S', s4, refrigerant)
            T4 = CP.PropsSI('T', 'P', P_low, 'H', h4, refrigerant)
            x4 = CP.PropsSI('Q', 'P', P_low, 'H', h4, refrigerant)

        StatePoint.objects.create(
            calculation=calc, point_number=4,
            temperature=T4 - 273.15, pressure=P_low / 1000,
            enthalpy=h4 / 1000, entropy=s4 / 1000, quality=x4
        )

        # Calculate COP
        q_evap = h1 - h4  # Cooling effect
        w_comp = h2 - h1  # Compressor work
        w_turb = h3 - h4 if calc.expansion_device == 'turbine' else 0

        net_work = w_comp - w_turb
        cop = q_evap / net_work if net_work > 0 else 0

        calc.cop = cop
        calc.cooling_capacity = q_evap / 1000  # kJ/kg
        calc.save()

    def calculate_absorption(self, calc, refrigerant):
        # Simplified absorption cycle calculation
        T_evap = calc.evaporator_temp + 273.15
        T_cond = calc.condenser_temp + 273.15
        T_gen = calc.generator_temp + 273.15 if calc.generator_temp else T_cond + 20
        T_abs = calc.absorber_temp + 273.15 if calc.absorber_temp else T_evap + 10

        # Basic absorption cycle points (simplified)
        P_low = CP.PropsSI('P', 'T', T_evap, 'Q', 1, refrigerant)
        P_high = CP.PropsSI('P', 'T', T_cond, 'Q', 0, refrigerant)

        h1 = CP.PropsSI('H', 'T', T_evap, 'Q', 1, refrigerant)
        h2 = CP.PropsSI('H', 'T', T_cond, 'Q', 0, refrigerant)
        h3 = h2  # Throttling

        s1 = CP.PropsSI('S', 'T', T_evap, 'Q', 1, refrigerant)
        s2 = CP.PropsSI('S', 'T', T_cond, 'Q', 0, refrigerant)
        s3 = s2

        StatePoint.objects.create(
            calculation=calc, point_number=1,
            temperature=T_evap - 273.15, pressure=P_low / 1000,
            enthalpy=h1 / 1000, entropy=s1 / 1000, quality=1.0
        )
        StatePoint.objects.create(
            calculation=calc, point_number=2,
            temperature=T_cond - 273.15, pressure=P_high / 1000,
            enthalpy=h2 / 1000, entropy=s2 / 1000, quality=0.0
        )
        StatePoint.objects.create(
            calculation=calc, point_number=3,
            temperature=T_evap - 273.15, pressure=P_low / 1000,
            enthalpy=h3 / 1000, entropy=s3 / 1000
        )

        # Simplified COP calculation for absorption
        q_evap = h1 - h3
        q_gen = 2000000  # Simplified heat input
        cop = q_evap / q_gen if q_gen > 0 else 0

        calc.cop = cop
        calc.cooling_capacity = q_evap / 1000
        calc.save()


class CalculationListView(ListView):
    model = Calculation
    template_name = 'cycle_calculator/calculation_list.html'
    context_object_name = 'calculations'
    ordering = ['-created_at']


class CalculationDetailView(ListView):
    model = StatePoint
    template_name = 'cycle_calculator/calculation_detail.html'
    context_object_name = 'state_points'

    def get_queryset(self):
        calc_id = self.kwargs['pk']
        return StatePoint.objects.filter(calculation_id=calc_id).order_by('point_number')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calculation = Calculation.objects.get(id=self.kwargs['pk'])
        context['calculation'] = calculation

        # Generate diagrams
        try:
            refrigerant_name = calculation.refrigerant.coolprop_name
            diagrams = ThermodynamicDiagrams(refrigerant_name)

            # Convert state points to dict format
            state_points = []
            for point in self.get_queryset():
                state_points.append({
                    'temperature': point.temperature,
                    'pressure': point.pressure,
                    'enthalpy': point.enthalpy,
                    'entropy': point.entropy,
                    'quality': point.quality
                })

            # Generate diagrams
            context['ph_diagram'] = diagrams.create_ph_diagram(state_points)
            context['pv_diagram'] = diagrams.create_pv_diagram(state_points)
            context['ts_diagram'] = diagrams.create_ts_diagram(state_points)

        except Exception as e:
            print(f"Diagram generation error: {e}")
            context['diagram_error'] = str(e)

        return context
