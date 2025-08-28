import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import CoolProp.CoolProp as CP
from CoolProp.Plots import PropertyPlot
import io
import base64
from typing import Dict, List, Tuple
import warnings

warnings.filterwarnings('ignore')


class ThermodynamicDiagrams():
    """Enhanced class for generating high-quality thermodynamic diagrams"""

    def __init__(self, refrigerant_name: str):
        self.refrigerant = refrigerant_name
        plt.style.use('seaborn-v0_8')
        plt.rcParams.update({
            'font.size': 10,
            'font.weight': 'bold',
            'axes.labelweight': 'bold',
            'axes.titleweight': 'bold',
            'figure.facecolor': 'white',
            'axes.facecolor': 'white',
            'axes.edgecolor': 'black',
            'axes.linewidth': 1.2,
            'grid.alpha': 0.3,
            'lines.linewidth': 1.5
        })

    def create_ph_diagram(self, state_points: List[Dict], calculation_data: Dict = None) -> str:
        """Create detailed P-h diagram with enhanced isolines"""
        try:
            fig, ax = plt.subplots(figsize=(14, 10))

            # Get critical properties
            T_crit = CP.PropsSI('Tcrit', self.refrigerant)
            P_crit = CP.PropsSI('Pcrit', self.refrigerant)

            # Create temperature range for isotherms
            T_min = T_crit * 0.5
            T_max = T_crit * 1.2
            temperatures = np.linspace(T_min, T_max, 15)

            # Draw isotherms
            for T in temperatures:
                try:
                    if T < T_crit:
                        # Two-phase region
                        h_sat_liq = CP.PropsSI('H', 'T', T, 'Q', 0, self.refrigerant) / 1000
                        h_sat_vap = CP.PropsSI('H', 'T', T, 'Q', 1, self.refrigerant) / 1000
                        p_sat = CP.PropsSI('P', 'T', T, 'Q', 0, self.refrigerant) / 1000

                        # Saturated liquid line
                        ax.plot([h_sat_liq], [p_sat], 'b-', linewidth=2, alpha=0.8)
                        # Saturated vapor line
                        ax.plot([h_sat_vap], [p_sat], 'r-', linewidth=2, alpha=0.8)
                        # Constant temperature line in two-phase region
                        ax.plot([h_sat_liq, h_sat_vap], [p_sat, p_sat], 'g--',
                                linewidth=1.5, alpha=0.6)

                        # Superheated region
                        pressures = np.logspace(np.log10(p_sat), np.log10(P_crit / 1000), 50)
                        enthalpies = []
                        valid_pressures = []

                        for p in pressures:
                            try:
                                h = CP.PropsSI('H', 'T', T, 'P', p * 1000, self.refrigerant) / 1000
                                enthalpies.append(h)
                                valid_pressures.append(p)
                            except:
                                continue

                        if len(enthalpies) > 5:
                            ax.plot(enthalpies, valid_pressures, 'purple',
                                    linewidth=1, alpha=0.5)

                        # Label temperature
                        if len(enthalpies) > 0:
                            ax.annotate(f'{T - 273.15:.0f}°C',
                                        (enthalpies[-1], valid_pressures[-1]),
                                        fontsize=8, alpha=0.7, color='purple')

                except Exception as e:
                    continue

            # Draw quality lines
            qualities = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
            for quality in qualities:
                try:
                    T_range = np.linspace(T_min, T_crit * 0.95, 30)
                    enthalpies = []
                    pressures = []

                    for T in T_range:
                        try:
                            h = CP.PropsSI('H', 'T', T, 'Q', quality, self.refrigerant) / 1000
                            p = CP.PropsSI('P', 'T', T, 'Q', quality, self.refrigerant) / 1000
                            enthalpies.append(h)
                            pressures.append(p)
                        except:
                            continue

                    if len(enthalpies) > 5:
                        ax.plot(enthalpies, pressures, 'orange',
                                linewidth=1, alpha=0.6, linestyle='--')

                        # Label quality
                        mid_idx = len(enthalpies) // 2
                        ax.annotate(f'{quality:.1f}',
                                    (enthalpies[mid_idx], pressures[mid_idx]),
                                    fontsize=7, alpha=0.7, color='orange')

                except:
                    continue

            # Draw saturation dome
            try:
                T_sat_range = np.linspace(T_min, T_crit * 0.99, 100)
                h_sat_liq = []
                h_sat_vap = []
                p_sat = []

                for T in T_sat_range:
                    try:
                        h_l = CP.PropsSI('H', 'T', T, 'Q', 0, self.refrigerant) / 1000
                        h_v = CP.PropsSI('H', 'T', T, 'Q', 1, self.refrigerant) / 1000
                        p = CP.PropsSI('P', 'T', T, 'Q', 0, self.refrigerant) / 1000

                        h_sat_liq.append(h_l)
                        h_sat_vap.append(h_v)
                        p_sat.append(p)
                    except:
                        continue

                if len(h_sat_liq) > 10:
                    ax.plot(h_sat_liq, p_sat, 'b-', linewidth=3,
                            label='Saturated Liquid', alpha=0.8)
                    ax.plot(h_sat_vap, p_sat, 'r-', linewidth=3,
                            label='Saturated Vapor', alpha=0.8)

                    # Fill saturation dome
                    ax.fill_betweenx(p_sat, h_sat_liq, h_sat_vap,
                                     alpha=0.1, color='lightblue')
            except:
                pass

            # Plot cycle points
            if state_points:
                enthalpies = [point.get('enthalpy', 0) for point in state_points]
                pressures = [point.get('pressure', 0) for point in state_points]

                # Remove any invalid points
                valid_points = [(h, p) for h, p in zip(enthalpies, pressures)
                                if h > 0 and p > 0]

                if valid_points:
                    h_vals, p_vals = zip(*valid_points)

                    # Close the cycle
                    h_cycle = list(h_vals) + [h_vals[0]]
                    p_cycle = list(p_vals) + [p_vals[0]]

                    # Plot cycle
                    ax.plot(h_cycle, p_cycle, 'ko-', linewidth=4, markersize=10,
                            markerfacecolor='yellow', markeredgecolor='black',
                            markeredgewidth=2, label='Thermodynamic Cycle', zorder=10)

                    # Add point labels with better positioning
                    for i, (h, p) in enumerate(valid_points):
                        ax.annotate(f'  {i + 1}', (h, p), fontsize=14, fontweight='bold',
                                    color='darkred', ha='left', va='bottom',
                                    bbox=dict(boxstyle="round,pad=0.3",
                                              facecolor="white", alpha=0.8),
                                    zorder=11)

                    # Fill cycle area
                    ax.fill(h_cycle, p_cycle, alpha=0.2, color='yellow', zorder=5)

            ax.set_xlabel('Specific Enthalpy (kJ/kg)', fontsize=14, fontweight='bold')
            ax.set_ylabel('Pressure (kPa)', fontsize=14, fontweight='bold')
            ax.set_title(f'P-h Diagram for {self.refrigerant}\n'
                         f'(Critical: T={T_crit - 273.15:.1f}°C, P={P_crit / 1000:.0f} kPa)',
                         fontsize=16, fontweight='bold')
            ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
            ax.set_yscale('log')

            # Set reasonable limits
            if state_points and valid_points:
                h_vals, p_vals = zip(*valid_points)
                h_min, h_max = min(h_vals), max(h_vals)
                p_min, p_max = min(p_vals), max(p_vals)

                ax.set_xlim(h_min * 0.8, h_max * 1.2)
                ax.set_ylim(p_min * 0.5, p_max * 2.0)

            ax.legend(fontsize=12, loc='upper left')
            plt.tight_layout()

            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight',
                        facecolor='white', edgecolor='none')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)

            return image_base64

        except Exception as e:
            plt.close('all')
            return self._create_error_image(f"P-h Diagram Error: {str(e)}")

    def create_pv_diagram(self, state_points: List[Dict], calculation_data: Dict = None) -> str:
        """Create detailed P-V diagram with isotherms"""
        try:
            fig, ax = plt.subplots(figsize=(12, 10))

            # Get critical properties
            T_crit = CP.PropsSI('Tcrit', self.refrigerant)
            P_crit = CP.PropsSI('Pcrit', self.refrigerant)

            # Calculate specific volumes and pressures for state points
            volumes = []
            pressures = []
            temperatures = []

            for point in state_points:
                try:
                    p = point.get('pressure', 0) * 1000  # Convert kPa to Pa
                    h = point.get('enthalpy', 0) * 1000  # Convert kJ/kg to J/kg
                    t = point.get('temperature', 0) + 273.15  # Convert to K

                    # Calculate density then specific volume
                    density = CP.PropsSI('D', 'P', p, 'H', h, self.refrigerant)
                    v = 1 / density  # Specific volume

                    volumes.append(v)
                    pressures.append(point.get('pressure', 0))
                    temperatures.append(t)

                except Exception as e:
                    print(f"Error calculating volume for point: {e}")
                    continue

            # Draw isotherms
            if volumes and pressures:
                T_min = min(temperatures) * 0.9
                T_max = max(temperatures) * 1.1
                temp_range = np.linspace(T_min, min(T_max, T_crit * 0.95), 10)

                for T in temp_range:
                    try:
                        # Create pressure range
                        p_sat = CP.PropsSI('P', 'T', T, 'Q', 0, self.refrigerant)
                        p_range = np.logspace(np.log10(p_sat * 0.1),
                                              np.log10(min(P_crit * 0.9, p_sat * 10)), 50)

                        volumes_iso = []
                        pressures_iso = []

                        for p in p_range:
                            try:
                                density = CP.PropsSI('D', 'T', T, 'P', p, self.refrigerant)
                                v = 1 / density
                                volumes_iso.append(v)
                                pressures_iso.append(p / 1000)  # Convert to kPa
                            except:
                                continue

                        if len(volumes_iso) > 5:
                            ax.plot(volumes_iso, pressures_iso, 'gray',
                                    alpha=0.6, linewidth=1.5)

                            # Label temperature
                            if volumes_iso:
                                ax.annotate(f'{T - 273.15:.0f}°C',
                                            (volumes_iso[0], pressures_iso[0]),
                                            fontsize=9, alpha=0.8, color='gray')
                    except:
                        continue

                # Plot saturation dome
                try:
                    T_sat_range = np.linspace(T_min, min(T_crit * 0.99, T_max), 50)
                    v_sat_liq = []
                    v_sat_vap = []
                    p_sat_line = []

                    for T in T_sat_range:
                        try:
                            p_sat = CP.PropsSI('P', 'T', T, 'Q', 0, self.refrigerant)
                            rho_l = CP.PropsSI('D', 'T', T, 'Q', 0, self.refrigerant)
                            rho_v = CP.PropsSI('D', 'T', T, 'Q', 1, self.refrigerant)

                            v_sat_liq.append(1 / rho_l)
                            v_sat_vap.append(1 / rho_v)
                            p_sat_line.append(p_sat / 1000)
                        except:
                            continue

                    if len(v_sat_liq) > 10:
                        ax.plot(v_sat_liq, p_sat_line, 'b-', linewidth=3,
                                label='Saturated Liquid', alpha=0.8)
                        ax.plot(v_sat_vap, p_sat_line, 'r-', linewidth=3,
                                label='Saturated Vapor', alpha=0.8)

                        # Fill saturation dome
                        ax.fill_betweenx(p_sat_line, v_sat_liq, v_sat_vap,
                                         alpha=0.1, color='lightcyan')
                except:
                    pass

                # Plot cycle
                if len(volumes) == len(pressures):
                    # Close the cycle
                    volumes_cycle = volumes + [volumes[0]]
                    pressures_cycle = pressures + [pressures[0]]

                    # Plot cycle
                    ax.plot(volumes_cycle, pressures_cycle, 'ko-', linewidth=4,
                            markersize=12, markerfacecolor='lime',
                            markeredgecolor='darkgreen', markeredgewidth=2,
                            label='Thermodynamic Cycle', zorder=10)

                    # Fill cycle area (work area)
                    ax.fill(volumes_cycle, pressures_cycle, alpha=0.3,
                            color='lightgreen', label='Work Area', zorder=5)

                    # Add point labels
                    for i, (v, p) in enumerate(zip(volumes, pressures)):
                        ax.annotate(f'  {i + 1}', (v, p), fontsize=14, fontweight='bold',
                                    color='darkgreen', ha='left', va='bottom',
                                    bbox=dict(boxstyle="round,pad=0.3",
                                              facecolor="white", alpha=0.9),
                                    zorder=11)

                    # Calculate and display work (area under curve)
                    try:
                        work_area = 0
                        for i in range(len(volumes)):
                            j = (i + 1) % len(volumes)
                            work_area += 0.5 * (pressures[i] + pressures[j]) * \
                                         (volumes[j] - volumes[i])

                        ax.text(0.02, 0.98, f'Net Work ≈ {abs(work_area):.2f} kJ/kg',
                                transform=ax.transAxes, fontsize=12, fontweight='bold',
                                bbox=dict(boxstyle="round,pad=0.5",
                                          facecolor="lightyellow", alpha=0.8),
                                verticalalignment='top')
                    except:
                        pass

            ax.set_xlabel('Specific Volume (m³/kg)', fontsize=14, fontweight='bold')
            ax.set_ylabel('Pressure (kPa)', fontsize=14, fontweight='bold')
            ax.set_title(f'P-V Diagram for {self.refrigerant}',
                         fontsize=16, fontweight='bold')
            ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
            ax.set_yscale('log')
            ax.set_xscale('log')

            # Set reasonable limits
            if volumes and pressures:
                v_min, v_max = min(volumes), max(volumes)
                p_min, p_max = min(pressures), max(pressures)

                ax.set_xlim(v_min * 0.5, v_max * 2.0)
                ax.set_ylim(p_min * 0.5, p_max * 2.0)

            ax.legend(fontsize=12, loc='upper right')
            plt.tight_layout()

            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight',
                        facecolor='white', edgecolor='none')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)

            return image_base64

        except Exception as e:
            plt.close('all')
            return self._create_error_image(f"P-V Diagram Error: {str(e)}")

    def create_ts_diagram(self, state_points: List[Dict]) -> str:
        """Create detailed T-S diagram with isobars and quality lines"""
        try:
            fig, ax = plt.subplots(figsize=(12, 10))

            # Get critical properties
            T_crit = CP.PropsSI('Tcrit', self.refrigerant)
            P_crit = CP.PropsSI('Pcrit', self.refrigerant)

            # Extract cycle data
            entropies = []
            temperatures = []
            pressures = []

            for point in state_points:
                try:
                    entropy = point.get('entropy', 0)
                    temperature = point.get('temperature', 0) + 273.15
                    pressure = point.get('pressure', 0) * 1000  # Convert to Pa

                    entropies.append(entropy)
                    temperatures.append(temperature)
                    pressures.append(pressure)
                except:
                    continue

            # Draw isobars (constant pressure lines)
            if pressures:
                p_min = min(pressures) * 0.5
                p_max = max(pressures) * 2.0
                pressure_lines = np.logspace(np.log10(p_min), np.log10(p_max), 8)

                for p in pressure_lines:
                    try:
                        # Create entropy range
                        s_range = np.linspace(0.5, 3.0, 100)
                        temps_iso = []
                        entropies_iso = []

                        for s in s_range:
                            try:
                                temp = CP.PropsSI('T', 'P', p, 'S', s * 1000, self.refrigerant)
                                if temp > 200 and temp < T_crit * 1.5:  # Reasonable range
                                    temps_iso.append(temp)
                                    entropies_iso.append(s)
                            except:
                                continue

                        if len(temps_iso) > 10:
                            ax.plot(entropies_iso, temps_iso, 'purple',
                                    alpha=0.6, linewidth=1.5)

                            # Label pressure
                            if entropies_iso and temps_iso:
                                ax.annotate(f'{p / 1000:.0f} kPa',
                                            (entropies_iso[-1], temps_iso[-1]),
                                            fontsize=9, alpha=0.8, color='purple')
                    except:
                        continue

            # Draw saturation dome
            try:
                T_sat_range = np.linspace(T_crit * 0.5, T_crit * 0.99, 100)
                s_sat_liq = []
                s_sat_vap = []
                T_sat = []

                for T in T_sat_range:
                    try:
                        s_l = CP.PropsSI('S', 'T', T, 'Q', 0, self.refrigerant) / 1000
                        s_v = CP.PropsSI('S', 'T', T, 'Q', 1, self.refrigerant) / 1000

                        s_sat_liq.append(s_l)
                        s_sat_vap.append(s_v)
                        T_sat.append(T)
                    except:
                        continue

                if len(s_sat_liq) > 10:
                    ax.plot(s_sat_liq, T_sat, 'b-', linewidth=3,
                            label='Saturated Liquid', alpha=0.8)
                    ax.plot(s_sat_vap, T_sat, 'r-', linewidth=3,
                            label='Saturated Vapor', alpha=0.8)

                    # Fill saturation dome
                    ax.fill_betweenx(T_sat, s_sat_liq, s_sat_vap,
                                     alpha=0.1, color='lightpink')
            except:
                pass

            # Draw quality lines
            qualities = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
            for quality in qualities:
                try:
                    T_range = np.linspace(T_crit * 0.5, T_crit * 0.95, 30)
                    entropies_q = []
                    temps_q = []

                    for T in T_range:
                        try:
                            s = CP.PropsSI('S', 'T', T, 'Q', quality, self.refrigerant) / 1000
                            entropies_q.append(s)
                            temps_q.append(T)
                        except:
                            continue

                    if len(entropies_q) > 5:
                        ax.plot(entropies_q, temps_q, 'orange',
                                linewidth=1, alpha=0.6, linestyle='--')

                        # Label quality
                        mid_idx = len(entropies_q) // 2
                        if mid_idx < len(entropies_q):
                            ax.annotate(f'{quality:.1f}',
                                        (entropies_q[mid_idx], temps_q[mid_idx]),
                                        fontsize=8, alpha=0.7, color='orange')
                except:
                    continue

            # Plot cycle
            if entropies and temperatures:
                # Close the cycle
                entropies_cycle = entropies + [entropies[0]]
                temperatures_cycle = temperatures + [temperatures[0]]

                # Plot cycle
                ax.plot(entropies_cycle, temperatures_cycle, 'ko-',
                        linewidth=4, markersize=12, markerfacecolor='cyan',
                        markeredgecolor='darkblue', markeredgewidth=2,
                        label='Thermodynamic Cycle', zorder=10)

                # Fill cycle area
                ax.fill(entropies_cycle, temperatures_cycle, alpha=0.3,
                        color='lightcyan', label='Cycle Area', zorder=5)

                # Add point labels
                for i, (s, t) in enumerate(zip(entropies, temperatures)):
                    ax.annotate(f'  {i + 1}', (s, t), fontsize=14, fontweight='bold',
                                color='darkblue', ha='left', va='bottom',
                                bbox=dict(boxstyle="round,pad=0.3",
                                          facecolor="white", alpha=0.9),
                                zorder=11)

                # Calculate and display entropy generation
                try:
                    entropy_change = max(entropies) - min(entropies)
                    ax.text(0.02, 0.98, f'ΔS_cycle ≈ {entropy_change:.3f} kJ/kg·K',
                            transform=ax.transAxes, fontsize=12, fontweight='bold',
                            bbox=dict(boxstyle="round,pad=0.5",
                                      facecolor="lightcyan", alpha=0.8),
                            verticalalignment='top')
                except:
                    pass

            ax.set_xlabel('Specific Entropy (kJ/kg·K)', fontsize=14, fontweight='bold')
            ax.set_ylabel('Temperature (K)', fontsize=14, fontweight='bold')
            ax.set_title(f'T-S Diagram for {self.refrigerant}',
                         fontsize=16, fontweight='bold')
            ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)

            # Set reasonable limits
            if entropies and temperatures:
                s_min, s_max = min(entropies), max(entropies)
                t_min, t_max = min(temperatures), max(temperatures)

                ax.set_xlim(s_min * 0.8, s_max * 1.2)
                ax.set_ylim(t_min * 0.95, t_max * 1.05)

            ax.legend(fontsize=12, loc='upper left')
            plt.tight_layout()

            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight',
                        facecolor='white', edgecolor='none')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)

            return image_base64

        except Exception as e:
            plt.close('all')
            return self._create_error_image(f"T-S Diagram Error: {str(e)}")

    def _create_error_image(self, error_msg: str) -> str:
        """Create an enhanced error image"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, f"⚠️ خطا در تولید نمودار\n\n{error_msg}\n\n"
                          f"لطفاً پارامترهای ورودی را بررسی کنید",
                ha='center', va='center', fontsize=14, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightcoral", alpha=0.8),
                color='darkred')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)

        return image_base64
