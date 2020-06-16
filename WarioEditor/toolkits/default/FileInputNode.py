from wario import Node

###################################################################################################
#
###################################################################################################

class ConsoleInputNode(InputNode):
    """ this is an input node where each item is recieved from user input on the command line """

    def input_prompt(self):
        """ prompt the user with instructions on the command line """
