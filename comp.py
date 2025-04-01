import math

class SolarHarvester:
    """
    SolarHarvester model to simulate energy harvesting from solar cells.
    """
    def __init__(self, Area, a=7.94e-7, b=0.0108, c=-0.0287):
        """
        Initialize a SolarHarvester instance.

        Parameters:
        Area (float): Area of solar cell [cm^2].
        """
        self.Area = Area  # Area of the solar cell in cm^2
        self.a = a        # Regression parameter a
        self.b = b        # Regression parameter b
        self.c = c        # Regression parameter c
        self.P = 0        # Real-time power output in Watts

    def compute_power(self, env1):
        """
        Compute the real-time power output of the solar harvester.

        Parameters:
        env1 (float): Global irradiance [W/m^2].

        Updates:
        self.P: Real-time power output in Watts.
        """
        G = env1  # Global irradiance
        Pm = max(0, -self.a * G**2 + self.b * G + self.c)

        # Compute power output and convert to Watts
        self.P = Pm * self.Area / 1000


class Sensor:
    """
    Sensor class to simulate power requirements of a sensor.
    """
    def __init__(self, Tp, Ta, Ps, Pa, Ph):
        """
        Initialize a Sensor instance.

        Parameters:
        Tp (float): Period of the sensor [s].
        Ta (float): Time interval of active mode [s].
        Ps (float): Power of sleeping mode [mW].
        Pa (float): Power of active mode [mW].
        Ph (float): Power of high workload mode [mW].
        """
        self.Tp = Tp  # Period of the sensor
        self.Ta = Ta  # Time interval of active mode
        self.Ps = Ps  # Power of sleeping mode
        self.Pa = Pa  # Power of active mode
        self.Ph = Ph  # Power of high workload mode
        self.P = 0    # Real power of the sensor [W]

    def compute_power(self, event, Sys_t):
        """
        Compute the power requirement of the sensor based on its state.

        Parameters:
        event (int): Current event state (0 for normal, other values for high workload).
        Sys_t (float): Current system time [s].

        Updates:
        self.P: The power requirement of the sensor [W].
        """
        sensor_t = Sys_t % self.Tp  # Compute the relative time within the sensor's period

        if event == 0:  # Normal operation
            if self.Tp / 2 <= sensor_t < self.Tp / 2 + self.Ta:
                self.P = self.Pa / 1000  # Active mode (convert mW to W)
            else:
                self.P = self.Ps / 1000  # Sleeping mode (convert mW to W)
        else:  # High workload mode
            self.P = self.Ph / 1000  # High workload mode (convert mW to W)


class SuperCapacitor:
    """
    SuperCapacitor model to simulate charging and discharging behavior.
    """
    def __init__(self, Vm=5, Rr=1.0857, C=1, Voc=None):
        """
        Initialize a SuperCapacitor instance.

        Parameters:
        Vm (float): Maximum voltage (V). Default is 5.
        Rr (float): Internal resistance (Ohm). Default is 1.0857.
        C (float): Capacitance (F). Default is 0.1225.
        Voc (float): Initial open circuit voltage (V). Default is Vm (fully charged).
        """
        # ----- Properties of SuperCapacitor -----
        self.Vm = Vm       # Maximum voltage (V)
        self.Rr = Rr       # Internal resistance (Ohm)
        self.C = C         # Capacitance (F)
        
        # ----- Initial state parameters -----
        self.Voc = Voc if Voc is not None else Vm  # Open circuit voltage (V). Default is Vm.
        self.Soc = self.Voc / self.Vm              # State of charge (ratio between 0 and 1)
        self.state = 2  # 0: out of charge, 1: normal, 2: fully charged
        self.Psc = 0    # Current power (W)

    def update(self, Psys, dt):
        """
        Update the capacitor state based on power and time step.

        Parameters:
        Psys (float): Power applied to the capacitor (W).
                      Psys > 0: discharging, Psys < 0: charging.
        dt (float): Time step (s).
        """
        self.Psc = Psys
        
        # Check for overcharging or discharging
        if Psys > 0 and self.state == 0:
            # print("The SC is out of charge!")
            return
        elif Psys < 0 and self.state == 2:
            # print("The SC is full of charge!")
            return
        
        # Calculate new voltage
        try:
            Vocn = math.sqrt(self.Voc**2 - 2 * Psys * dt / self.C)
        except ValueError:
            # print("Error: Voltage calculation resulted in complex value.")
            return
        
        Q1 = self.C * abs(Vocn - self.Voc)  # Charge change
        Er = Q1**2 * self.Rr / dt           # Energy loss in resistance
        Ec = Er + Psys * dt                 # Total energy change
        try:
            self.Voc = math.sqrt(self.Voc**2 - 2 * Ec / self.C)  # Update voltage
        except ValueError:
            self.Voc = 0  # Adjust voltage to valid range
        
        # Update state of charge
        self.Soc = self.Voc / self.Vm
        
        # Update state
        if self.Voc >= self.Vm:
            self.state = 2  # Fully charged
            self.Voc = self.Vm  # Clamp to maximum voltage
        elif self.Voc <= self.Vm / 4:
            self.state = 0  # Out of charge
            self.Voc = self.Vm / 4  # Clamp to minimum voltage
        else:
            self.state = 1  # Normal


class LiBattery:
    """LiBattery: Lithium-ion battery model."""
    
    def __init__(self, A0, t_c=None, t_d=None):
        # Cycle-life parameters
        self.z = 0.430348812891015
        self.b_para = [1.0519, -5.6896]
        self.Ar = 0.0088

        # Initial electrical parameters
        self.A0 = A0  # Original capacity of battery (Ah)
        self.Rr = 0.46  # Inner resistance of battery (Ohm)
        self.t_c = t_c or [0.832784949290123, 0.00950742937440156, 0.986933683934508,
                           1.91017763008209, 0.366569502392137, 1.00215219026646, 1.57676233212954]
        self.t_d = t_d or [0.476542280050523, 0.0531424828486832, 0.968130028634588,
                           2.09592651158253, 1.35223313396928, 4.34427534146120, 1.48772171109281]

        # State of Battery
        self.Soc = 0.75  # State of charge (initially 75%)
        self.Voc = None  # Voltage of battery (V)
        self.I = 0  # Current (A)
        self.P_check = 0  # Power demand check
        self.Qloss = 0.01  # Capacity loss
        self.state = 1  # 1 = normal, 0 = out of charge, 2 = fully charged, -1 = out of life

        self.update_voc(discharge=True)

    def update_voc(self, discharge=True):
        """Update open-circuit voltage (Voc) based on SOC."""
        params = self.t_d if discharge else self.t_c
        self.Voc = (
            params[0] * (1 - (params[1] * (1 - self.Soc) / (1 - params[2] * (1 - self.Soc)))) +
            params[3] * (1 - (params[4] * (1 - self.Soc) / (1 + params[5] * (1 - self.Soc)))) +
            params[6]
        )

    def update(self, Pdemand, dt):
        """
        Update battery state based on power demand (Pdemand) and time step (dt in seconds).
        Pdemand > 0: discharge
        Pdemand < 0: charge
        """
        self.P_check = Pdemand
        
        if Pdemand > 0 and self.state == 0:
            self.I = 0
            self.Qloss = 0.1  # Battery is out of charge
            # print("The battery is out of charge!")
        
        elif Pdemand < 0 and self.state == 2:
            self.I = 0  # Battery is fully charged
        
        elif self.state != -1:
            # Update voltage for charging/discharging
            self.update_voc(discharge=(Pdemand > 0))

            # Solve for current (I) using quadratic equation
            try:
                self.I = -(self.Voc - math.sqrt(self.Voc**2 - 4 * self.Rr * Pdemand)) / (2 * self.Rr)
            except ValueError:
                self.I = 0
                # print("Invalid power demand or voltage state.")

            # Capacity throughput (Ah) and SOC update
            Ah = self.I * dt / 3600  # Ah-throughput in dt
            self.Soc += Ah / ((1 - self.Qloss) * self.A0)

            # Cycle-life degradation
            C = abs(self.I / self.A0)
            b = self.b_para[0] * C + self.b_para[1]
            Ahr = abs(Ah / self.A0 * self.Ar)
            dQloss = Ahr * self.z * math.exp(b / self.z) * self.Qloss**((self.z - 1) / self.z)
            self.Qloss += dQloss

            # Update battery state
            if self.Qloss >= 0.90:
                self.state = -1
                # print("The battery is out of life!")
            elif self.Soc >= (1 - self.Qloss) or self.Soc >= 0.99:
                self.state = 2
            elif self.Soc <= 0.10:
                self.state = 0
                # print("The battery is out of charge!")
            else:
                self.state = 1

class Energysystem:
    """
    Energysystem: A composite micro-energy system simulation.
    """

    def __init__(self, dt, sensor, supercapacitor, battery, solar_harvester, Ps_a, management, k):
        """
        Initialize the energy system.

        Parameters:
        dt (float): Time step (s).
        sensor (Sensor): Sensor object.
        supercapacitor (SuperCapacitor): SuperCapacitor object.
        battery (LiBattery): LiBattery object.
        solar_harvester (SolarHarvester): SolarHarvester object.
        Ps_a (float): Average power of the sensor [W].
        management (int): Energy management strategy (1-7).
        k (list): Energy management parameters.
        """
        self.dt = dt
        self.sensor = sensor
        self.supercapacitor = supercapacitor
        self.battery = battery
        self.supercapacitor.Voc = self.battery.Voc  # Initialize SC voltage to match battery
        self.solar_harvester = solar_harvester
        self.management = management
        self.Ps_a = Ps_a
        self.k = k
        self.k_adaptive = [
            k[0] * Ps_a,
            k[1] * supercapacitor.Vm,
            k[2] * Ps_a,
            k[3],
            k[4],
        ]
        self.DC_Eff_Sensor = 0.9
        self.DC_Eff_Solar = 0.9
        self.P_batt = 0
        self.P_sc = 0
        self.P_demand = 0
        self.yita = 1
        self.Sys_t = 0  # System time
        self.state = 1  # 1 = normal, 0 = out of charge, -1 = out of life

    def update(self, event, env):
        """
        Update the energy system at the current time step.

        Parameters:
        event (int): Current event state (0 for normal, other values for high workload).
        env (float): Global irradiance [W/m^2] for the solar harvester.

        Returns:
        List: [P_demand, P_sensor, P_solar, P_SC, P_Bat]
        """
        if self.state >= 0:
            self.Sys_t += self.dt
            # Compute power requirements
            self.sensor.compute_power(event, self.Sys_t)
            self.solar_harvester.compute_power(env)
            Psensor = self.sensor.P
            Psolar = self.solar_harvester.P

            # Compute power demand
            Pdemand = (Psensor / 0.9) - (Psolar * 0.9)  # DC/DC efficiencies for sensor and solar
            self.P_demand = Pdemand
            # # print(f"Pdemand is {Pdemand}")

            # Use energy manager to allocate power
            P_SC, P_Bat = self.energy_manager(Pdemand)

            # Update supercapacitor and battery
            self.supercapacitor.update(P_SC, self.dt)
            self.battery.update(P_Bat, self.dt)

            # Judge system state
            self.judge_state()

            return [Pdemand, Psensor, Psolar, P_SC, P_Bat]

    def energy_manager(self, Pdemand):
        """
        Energy management strategy to allocate power between supercapacitor and battery.

        Parameters:
        Pdemand (float): Power demand (W).

        Returns:
        Tuple: (P_SC, P_Bat) -> Power allocated to supercapacitor and battery.
        """
        P_Bat = 0
        P_SC = 0

        if self.management == 1:  # Strategy 1: Only Battery
            P_Bat = Pdemand

        elif self.management == 2:  # Strategy 2: SuperCapacitor First
            if (Pdemand > 0 and self.supercapacitor.state != 0) or \
               (Pdemand < 0 and self.supercapacitor.state != 2):
                P_SC = Pdemand
            else:
                P_Bat = Pdemand

        elif self.management == 3:  # Strategy 3: Voltage Controlled
            if ((Pdemand > 0 and self.supercapacitor.Voc > self.battery.Voc) or
                    (Pdemand < 0 and self.supercapacitor.Voc < self.battery.Voc)):
                P_SC = Pdemand
            else:
                P_Bat = Pdemand

        elif self.management == 4:  # Strategy 4: Improved Parallel Strategy
            if Pdemand > 0:
                if self.solar_harvester.P > 0.5 * self.Ps_a:
                    if self.supercapacitor.Voc - self.battery.Voc <= -0.9 and self.supercapacitor.state != 0:
                        P_Bat = Pdemand
                    else:
                        P_SC = 0.5 * self.supercapacitor.C * (self.supercapacitor.Voc - self.battery.Voc + 0.9)**2 / self.dt
                        if P_SC > Pdemand:
                            P_SC = Pdemand
                        else:
                            P_Bat = Pdemand - P_SC
                else:
                    if self.supercapacitor.Voc > self.battery.Voc:
                        P_SC = 0.5 * self.supercapacitor.C * (self.supercapacitor.Voc - self.battery.Voc)**2 / self.dt
                        if P_SC > Pdemand:
                            P_SC = Pdemand
                        else:
                            P_Bat = Pdemand - P_SC
                    else:
                        P_SC = -0.2 * self.Ps_a
                        P_Bat = Pdemand - P_SC
            else:
                if self.supercapacitor.Voc - self.battery.Voc >= 0.3:
                    P_Bat = Pdemand
                else:
                    P_SC = -0.5 * self.supercapacitor.C * (self.supercapacitor.Voc - self.battery.Voc - 0.3)**2 / self.dt
                    if P_SC < Pdemand:
                        P_SC = Pdemand
                    else:
                        P_Bat = Pdemand - P_SC

        elif self.management == 5:  # Strategy 5: Rule-based Strategy
            if self.solar_harvester.P < self.k_adaptive[0]:
                if self.supercapacitor.Voc < self.k_adaptive[1]:
                    P_Bat = self.k_adaptive[2]
                    P_SC = -P_Bat
            if Pdemand > 0:
                if self.supercapacitor.state != 0:
                    P_SC += Pdemand
                else:
                    P_Bat += Pdemand
            else:
                if self.supercapacitor.state != 2:
                    P_SC += Pdemand
                else:
                    P_Bat += Pdemand

        elif self.management == 6:  # Strategy 6: Adaptive Rule-based Strategy
            if self.solar_harvester.P < self.k_adaptive[0]:
                if self.supercapacitor.Voc < self.k_adaptive[1]:
                    P_Bat = self.k_adaptive[2]
                    P_SC = -P_Bat
            if Pdemand > 0:
                if self.supercapacitor.state != 0:
                    P_SC += Pdemand
                else:
                    P_Bat += Pdemand
            else:
                if self.supercapacitor.state != 2:
                    P_SC += Pdemand
                else:
                    if Pdemand < -5 * self.Ps_a:
                        Pdemand = min(
                            (1 - self.k_adaptive[3] * self.k_adaptive[4] - (1 - self.k_adaptive[4]) * self.battery.Soc) /
                            (1 - self.k_adaptive[3]), 1) * Pdemand
                        self.yita = min(
                            (1 - self.k_adaptive[3] * self.k_adaptive[4] - (1 - self.k_adaptive[4]) * self.battery.Soc) /
                            (1 - self.k_adaptive[3]), 1)
                    P_Bat += Pdemand

        self.P_batt = P_Bat
        self.P_sc = P_SC
        return P_SC, P_Bat

    def judge_state(self):
        """
        Judge the state of the system based on the battery and supercapacitor.
        """
        if self.battery.state == -1:
            self.state = -1  # Battery is out of life
        elif self.battery.state == 0 and self.supercapacitor.state == 0:
            self.state = 0  # System is out of charge