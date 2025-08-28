from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import Refrigerant, Calculation
from .calculations.refrigerants import CoolPropRefrigerant
from .calculations.cycles import VaporCompressionCycle
import plotly.graph_objects as go
import plotly.offline as pyo


def calculate(request):
    refrigerants = Refrigerant.objects.all()

    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            refrigerant_id = request.POST.get('refrigerant')
            t_evap = float(request.POST.get('t_evap'))
            t_cond = float(request.POST.get('t_cond'))
            mass_flow = float(request.POST.get('mass_flow'))

            # Validation
            if not all([name, refrigerant_id, t_evap, t_cond, mass_flow]):
                raise ValueError("همه فیلدها باید پر شوند")

            if t_evap >= t_cond:
                raise ValueError("دمای اواپراتور باید کمتر از دمای کندانسور باشد")

            if mass_flow <= 0:
                raise ValueError("نرخ جرمی باید مثبت باشد")

            # Get refrigerant
            refrigerant_obj = get_object_or_404(Refrigerant, id=refrigerant_id)

            # Initialize refrigerant and cycle
            refrigerant = CoolPropRefrigerant(refrigerant_obj.coolprop_name)
            cycle = VaporCompressionCycle(
                refrigerant=refrigerant,
                t_evap=t_evap,
                t_cond=t_cond,
                mass_flow=mass_flow
            )

            # Calculate results
            results = cycle.calculate()

            # Save to database
            calc = Calculation.objects.create(
                name=name,
                refrigerant=refrigerant_obj,
                t_evap=t_evap,
                t_cond=t_cond,
                mass_flow=mass_flow,
                cop_ideal=results['cop_ideal'],
                cop_actual=results['cop_actual']
            )

            # Generate diagram
            diagram = create_ph_diagram(results, refrigerant_obj.name)

            return render(request, 'cycle_calculator/results.html', {
                'calc': calc,
                'results': results,
                'diagram': diagram
            })

        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'خطا در محاسبه: {str(e)}')

    return render(request, 'cycle_calculator/calculate.html', {
        'refrigerants': refrigerants
    })


def create_ph_diagram(results, refrigerant_name):
    """Create enhanced P-h diagram"""
    points = results['points']
    pressures = results['pressures']

    # Cycle points
    h_vals = [points['h1'], points['h2'], points['h3'], points['h4'], points['h1']]
    p_vals = [pressures['p_evap'], pressures['p_cond'], pressures['p_cond'], pressures['p_evap'], pressures['p_evap']]

    fig = go.Figure()

    # Add cycle line with gradient colors
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']

    for i in range(len(h_vals) - 1):
        fig.add_trace(go.Scatter(
            x=[h_vals[i], h_vals[i + 1]],
            y=[p_vals[i], p_vals[i + 1]],
            mode='lines+markers',
            name=f'Process {i + 1}-{i + 2 if i < 3 else 1}',
            line=dict(color=colors[i], width=4),
            marker=dict(size=12, color=colors[i])
        ))

    # Add point labels with annotations
    labels = ['1 (Evaporator Out)', '2 (Compressor Out)', '3 (Condenser Out)', '4 (Expansion Valve Out)']
    for i, (h, p, label) in enumerate(zip(h_vals[:-1], p_vals[:-1], labels)):
        fig.add_annotation(
            x=h, y=p,
            text=f"<b>{label}</b><br>h={h:.1f} kJ/kg<br>P={p:.1f} kPa",
            showarrow=True,
            arrowhead=2,
            arrowsize=1.5,
            arrowwidth=2,
            arrowcolor=colors[i],
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor=colors[i],
            borderwidth=2,
            font=dict(size=10)
        )

    fig.update_layout(
        title=dict(
            text=f'<b>نمودار P-h برای {refrigerant_name}</b>',
            x=0.5,
            font=dict(size=18)
        ),
        xaxis=dict(
            title='<b>آنتالپی (kJ/kg)</b>',
            gridcolor='lightgray',
            showgrid=True
        ),
        yaxis=dict(
            title='<b>فشار (kPa)</b>',
            gridcolor='lightgray',
            showgrid=True
        ),
        font=dict(family="Tahoma", size=12),
        width=900,
        height=650,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='rgba(248,249,250,1)',
        paper_bgcolor='white'
    )

    return pyo.plot(fig, output_type='div', include_plotlyjs=False)


def get_calculations(request):
    """Get user calculations history"""
    calculations = Calculation.objects.all().order_by('-created_at')[:10]
    return render(request, 'cycle_calculator/history.html', {
        'calculations': calculations
    })
