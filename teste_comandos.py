from printers import Printer
from modules import Head

printer = Printer.create_printer_standard_from_parts_dimensions(length_x=380, length_y=400, length_z=50)
configuration = [2]
for pos_y in range(len(configuration)):
    for pos_x in range(configuration[pos_y]):
        aux_head = Head.create_standard_head()
        aux_head.set_position_in_rails(pos_x=pos_x, pos_y=pos_y)
        aux_head.calculate_origin_point(nr_rails=len(configuration), nr_heads_in_rail=configuration[pos_y])
        aux_head.place_head_in_point(point=aux_head.reference_point)
        aux_head.calculate_max_x_reference_point(nr_heads_in_rail=configuration[pos_y], length_x=printer.length_x)
        aux_head.calculate_safe_range(nr_rails=len(configuration))
        aux_head.calculate_soft_limits_from_reference_points()
        aux_head.create_safe_area(nr_rails=len(configuration))
        aux_head.create_unsafe_area(nr_rails=len(configuration))

        printer.add_head_to_printer(aux_head)

printer.set_heads_position_on_rails()
printer.update_printer_dimensions()
printer.place_heads_in_home_point()
printer.calculate_rails_build_area()
printer.calculate_neighbours_heads()


##
printer.set_com_ports(["COM3", "COM4"])
#printer.list_of_heads[0].material_id = 0
#printer.list_of_heads[1].material_id = 1

h1 = printer.list_of_heads[0]
h2 = printer.list_of_heads[1]


h1.connect_to_serial(h1.serial_port)
h2.connect_to_serial(h2.serial_port)

'''
h1.flush_start_messages()
message = h1.read_serial_message(show=False)
#print(message)


h1.add_instruction_to_queue("G28\n")
h1.send_next_instruction(show=True)
h1.read_serial_message(show=True)
'''


h2.flush_start_messages()
message = h2.read_serial_message(show=False)
#print(message)

#h2.add_instruction_to_queue("G28\n")

#h2.send_next_instruction(show=True)
#h2.read_serial_message(show=True)

h2.add_instruction_to_queue("G28\n")
h2.send_next_instruction(show=True)
#h2.read_serial_message(show=True)
h2.add_instruction_to_queue("G0 Y10\n")
h2.send_next_instruction(show=False)
h2.read_serial_message(show=True)




#h1.home_module_with_z()
#h1.home_modules_with_bed_leveling()
#input("Clica ok para continuar")

#h1.add_instruction_to_queue("M420 S1\n")
#h1.send_next_instruction(show=True)
#h1.read_serial_message(show=False)


# for instruction in end_gcode:
# a = [s.add_instruction_to_queue(instruction) for s in self.list_of_heads]
# s = [s.send_next_instruction(show=True) for s in self.list_of_heads]
# r = [r.read_serial_message(show=False) for r in self.list_of_heads]


print("")
#
# self.home_modules_with_z()
