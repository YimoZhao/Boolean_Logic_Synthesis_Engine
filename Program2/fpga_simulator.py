class LUT:
    def __init__(self, id, max_inputs, function=None):
        self.id = id
        self.max_inputs = max_inputs
        self.function = function
        self.connections = []

    def assign_function(self, function):
        self.function = function

    def add_connection(self, lut):
        self.connections.append(lut)

    def display(self):
        connected_to = ', '.join(str(lut.id) for lut in self.connections)
        return f"LUT {self.id}: Function: {self.function if self.function else 'Not assigned'} | Connected to: [{connected_to}]"


class FPGA:
    def __init__(self, num_luts, lut_input_type):
        self.luts = [LUT(id, lut_input_type) for id in range(num_luts)]
        self.external_inputs = {}
        self.external_outputs = {}
        self.total_connections = 0

    def assign_functions_to_luts(self, functions):
        for i, function in enumerate(functions):
            if i < len(self.luts):
                self.luts[i].assign_function(function)

    def connect_luts(self, connections):
        for source_id, target_ids in connections.items():
            if 0 <= source_id < len(self.luts):
                for target_id in target_ids:
                    if 0 <= target_id < len(self.luts):
                        self.luts[source_id].add_connection(self.luts[target_id])
                        self.total_connections += 1

    def assign_external_inputs(self, input_assignments):
        self.external_inputs = input_assignments

    def assign_external_outputs(self, output_assignments):
        self.external_outputs = output_assignments

    def display_all_lut_assignments(self):
        for lut in self.luts:
            print(lut.display())

    def display_lut_assignment(self, lut_id):
        if 0 <= lut_id < len(self.luts):
            print(self.luts[lut_id].display())
        else:
            print("Invalid LUT ID")

    def display_external_input_assignments(self):
        if not self.external_inputs:
            print("No external inputs assigned.")
            return
        for var, lut_id in self.external_inputs.items():
            print(f"External Variable '{var}' is assigned to LUT {lut_id}")

    def display_external_output_assignments(self):
        if not self.external_outputs:
            print("No external outputs assigned.")
            return
        for lut_id, var in self.external_outputs.items():
            print(f"LUT {lut_id}'s output is assigned to External Variable '{var}'")

    def generate_bitstream(self):
        """Generate a bitstream to program the FPGA."""
        bitstream = "FPGA Configuration Bitstream\n"
        bitstream += "--------------------------\n"
        bitstream += "Functions:\n"
        for lut in self.luts:
            bitstream += f"  LUT {lut.id}: {lut.function if lut.function else 'None'}\n"

        bitstream += "\nConnections:\n"
        for lut in self.luts:
            connected_to = ', '.join(str(lut_c.id) for lut_c in lut.connections)
            bitstream += f"  LUT {lut.id} -> {connected_to}\n"

        bitstream += "\nExternal Inputs:\n"
        for var, lut_id in self.external_inputs.items():
            bitstream += f"  '{var}' -> LUT {lut_id}\n"

        bitstream += "\nExternal Outputs:\n"
        for lut_id, var in self.external_outputs.items():
            bitstream += f"  LUT {lut_id} -> '{var}'\n"

        return bitstream

    def calculate_memory_usage(self):
        """Calculate and return an estimated memory usage for the FPGA configuration."""
        memory_per_lut = 128  # Example: 128 bytes per LUT (arbitrary)
        memory_per_connection = 32  # Example: 32 bytes per connection (arbitrary)
        total_memory = memory_per_lut * len(self.luts) + memory_per_connection * self.total_connections
        return total_memory

    def resource_allocation_summary(self):
        """Generate a resource allocation summary."""
        num_used_luts = sum(1 for lut in self.luts if lut.function is not None)
        percent_luts_used = (num_used_luts / len(self.luts)) * 100
        percent_connections_used = (self.total_connections / (len(self.luts) * (len(self.luts) - 1))) * 100
        total_memory = self.calculate_memory_usage()

        summary = "Resource Allocation Summary\n"
        summary += "--------------------------\n"
        summary += f"Percentage of LUTs Used: {percent_luts_used:.2f}%\n"
        summary += f"Percentage of Connections Used: {percent_connections_used:.2f}%\n"
        summary += f"Total Memory Required: {total_memory} bytes\n"
        return summary


# Functions to handle connectivity
def create_full_connectivity(fpga):
    for lut in fpga.luts:
        connected_luts = [other_lut for other_lut in fpga.luts if other_lut.id != lut.id]
        lut.connections = connected_luts

def create_partial_connectivity(fpga, connection_data):
    for source_id, target_ids in connection_data.items():
        if 0 <= source_id < len(fpga.luts):
            for target_id in target_ids:
                if 0 <= target_id < len(fpga.luts):
                    fpga.luts[source_id].add_connection(fpga.luts[target_id])
                    fpga.total_connections += 1

def read_logic_expressions(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]


if __name__ == "__main__":
    num_luts = 4
    lut_input_type = 4
    connectivity_type = "full"  # or "partial"
    logic_expressions_file = 'input.eqn'

    fpga = FPGA(num_luts, lut_input_type)

    logic_expressions = read_logic_expressions(logic_expressions_file)
    fpga.assign_functions_to_luts(logic_expressions)

    if connectivity_type == "full":
        create_full_connectivity(fpga)
    elif connectivity_type == "partial":
        # Define partial connections here
        partial_connections = {}
        create_partial_connectivity(fpga, partial_connections)

    # Define external inputs and outputs
    external_inputs = {'X': 0, 'Y': 1}  # Example
    external_outputs = {2: 'Z', 3: 'W'}  # Example
    fpga.assign_external_inputs(external_inputs)
    fpga.assign_external_outputs(external_outputs)

    # Display all information
    print("\nAll LUT Assignments with Connections:")
    fpga.display_all_lut_assignments()
    print("\nExternal Input Assignments:")
    fpga.display_external_input_assignments()
    print("\nExternal Output Assignments:")
    fpga.display_external_output_assignments()
    print("\nGenerated Bitstream:")
    print(fpga.generate_bitstream())
    print("\nResource Allocation Summary:")
    print(fpga.resource_allocation_summary())