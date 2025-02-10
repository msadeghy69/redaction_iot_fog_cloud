import random
import output
import mempool
import modification
from random import randrange

from Fobsim_my_architecture.main import run_with_bc

data = modification.read_file("Sim_parameters.json")


class Fog:
    def __init__(self, address, parent):
        self.address = address
        self.addressParent = parent
        self.tasks = []
        self.fog_tasks = []
        self.list_of_connected_users = set()
        self.identity_added_attributes = {}
        self.STOR_PLC = data["STOR_PLC(0=in the Fog,1=in the BC)"]
        self.local_storage = []


    def __str__(self):
        # اطمینان از بازگشت رشته
        tasks_details = [str(task) for task in self.tasks]
        connected_users_details = [str(user) for user in self.list_of_connected_users]

        return (f"Fog Address: {self.address}, Parent Cloud: {self.addressParent}, "
                f"Tasks: {tasks_details}, Connected Users: {connected_users_details}, "
                f"Identity Attributes: {self.identity_added_attributes}, STOR_PLC: {self.STOR_PLC}, "
                f"Local Storage: {self.local_storage}")

    def receive_tasks(self, tasks, sender):
        self.tasks.extend(tasks)
        self.list_of_connected_users.add(sender)




    def fog_smartcontract_authenticator(self, target_task, replace_task, fognodes, cloudnodes, address_self, address_parent, list_end_user):
 #add by ms
        result = False
        if address_self in self.list_of_connected_users:
            for obj in cloudnodes:
                if obj.address == self.addressParent:
                    result = obj.cloud_smartcontract_authenticator(target_task, replace_task,cloudnodes)
                    break
        if result :
            return True

    def send_tasks_to_cloud (self, list_of_cloud_nodes): #add by ms
        if run_with_bc:
            for obj in list_of_cloud_nodes:
                if obj.address == self.addressParent:

                    obj.receive_tasks(self.fog_tasks, self.address)

        else :
            cloud_broker = CloudBroker(cloudNodes)

            receive_tasks(self.tasks, self.address)


    def send_tasks_to_BC(self, user_informed):
        temporary_task = random.choice(self.tasks)
        if not user_informed:
            output.inform_of_fog_procedure(temporary_task[-1], self.STOR_PLC)
        if temporary_task[-1] in [1, 3, 4]:
            for task in self.tasks:
                if self.STOR_PLC == 1:
                    mempool.MemPool.append(task)
                else:
                    self.local_storage.append(task)
        if temporary_task[-1] == 2:
            for task in self.tasks:
                for letter in task[-2]:
                    if letter in ['+', '-']:
                        result = eval(task[-2])
                        produced_transaction = ['End-user address: ' + str(task[0]) + '.' + str(task[1]),
                                                'Requested computational task: ' + str(task[2]), 'Result: '
                                                + str(result), "Performed_by_fog_node_num: " + str(self.address)]
                        self.local_storage.append(produced_transaction)
                        break
                    elif letter in ['/', '*']:
                        mempool.MemPool.append(task)
                        break

    # متدهای اضافه‌شده از end_user.py
    def create_tasks(self, num_of_task_per_fog, blockchain_function, list_of_fog_users):
        if blockchain_function == 1:
            self.__apply_first_functionality(num_of_task_per_fog, blockchain_function)
        if blockchain_function == 2:
            self.__apply_second_functionality(num_of_task_per_fog, blockchain_function)
        if blockchain_function == 3:
            self.__apply_third_functionality(num_of_task_per_fog, list_of_fog_users, blockchain_function)
        if blockchain_function == 4:
            self.__apply_forth_functionality(blockchain_function)

    def __apply_first_functionality(self, num_of_task_per_fog, blockchain_function):
        for task_number in range(num_of_task_per_fog):
            self.fog_tasks.append([random.randint(0, 1000000), blockchain_function])
        output.txs_success(num_of_task_per_fog, self.addressParent, self.address)

    def __apply_second_functionality(self, num_of_task_per_fog, blockchain_function):
        operations = ['+', '-', '*', '/']
        for task_number in range(num_of_task_per_fog):
            operation = random.choice(operations)
            random_computational_task = str(randrange(1000000)) + operation + str(randrange(1000000))
            self.fog_tasks.append([self.addressParent, self.address, random_computational_task, blockchain_function])

    def __apply_third_functionality(self, num_of_task_per_fog, list_of_fog_users, blockchain_function):
        for task_number in range(num_of_task_per_fog):
            payment = randrange(round(data["Max_enduser_payment"], 0))
            receiver = random.choice(list_of_fog_users)
            receiver_parent_address = receiver.address
            receiver_individual_address = receiver.address
            proposed_transaction = [payment, self.addressParent, self.address, receiver_parent_address,
                                    receiver_individual_address, blockchain_function]
            self.fog_tasks.append(proposed_transaction)

    def __apply_forth_functionality(self, blockchain_function):
        add_new_attributes(self)
        proposed_transaction = [self.addressParent, self.address, self.identity_added_attributes, blockchain_function]
        self.fog_tasks.append(proposed_transaction)

def add_new_attributes(user):
    for key in user.identity_added_attributes:
        user.identity_added_attributes[key] = input(
            str(user.addressParent) + "." + str(user.addressSelf) + ": " + key + ">> ")