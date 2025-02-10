import random
import output
import mempool
import cloud_mempool
import modification

data = modification.read_file("Sim_parameters.json")


class Cloud:
    def __init__(self,address):
        """
        Initializes the Cloud layer with its own storage, tasks list, and VM configurations.
        """
        self.tasks = []  # List to store tasks sent to the cloud
        self.address = address
        self.vms = []  # List of virtual machines (VMs)
        self.STOR_PLC = data["STOR_PLC(0=in the Fog,1=in the BC)"]  # Storage policy
        self.local_storage = []  # Storage for processed tasks/results
        self.connected_fog_nodes = set()  # Fog nodes interacting with the cloud
        self.un_authorized_tasks = [] #add by ms
        self.authorized_end_device = []  # add by ms

    def __str__(self):
        tasks_details = [str(task) for task in self.tasks]
        connected_fogs_details = [str(fog) for fog in self.connected_fog_nodes]

        return (f"Cloud Address: {self.address}, Tasks: {tasks_details}, VMs: {self.vms}, "
                f"STOR_PLC: {self.STOR_PLC}, Local Storage: {self.local_storage}, "
                f"Connected Fog Nodes: {connected_fogs_details}")
    def create_vms(self, data):
        """
        Creates a pool of virtual machines (VMs) with random computational capacities.
        """
        print("The processor's computational power of the available VMs:")
        for i in range(data["num_vms"]):
            capacity = random.randint(data["minimum_capacity_of_vm"], data["maximum_capacity_of_vm"])
            self.vms.append(capacity)
            print(f"VM number ({i + 1}): {capacity}")

    def receive_tasks(self, tasks, sender):
        """
        Receives tasks from fog nodes and stores them in the cloud's task queue.
        """
        self.tasks.extend(tasks)
        self.connected_fog_nodes.add(sender)  # Keep track of which fog nodes sent tasks


    def send_cloud_tasks_to_BC(self, fog_informed):
        temporary_task = random.choice(self.tasks)
        if not fog_informed:
            output.inform_of_cloud_procedure(temporary_task[-1], self.STOR_PLC)
        if temporary_task[-1] in [1, 3, 4]:
            for task in self.tasks:
                if self.STOR_PLC == 1:
                    cloud_mempool.Cloud_MemPool.append(task)
                else:
                    self.local_storage.append(task)
        if temporary_task[-1] == 2:
            for task in self.tasks:
                for letter in task[-2]:
                    if letter in ['+', '-']:
                        result = eval(task[-2])
                        produced_transaction = ['Fog address: ' + str(task[0]) + '.' + str(task[1]),
                                                'Requested computational task: ' + str(task[2]), 'Result: '
                                                + str(result), "Performed_by_cloud_node_num: " + str(self.address)]
                        self.local_storage.append(produced_transaction)
                        break
                    elif letter in ['/', '*']:
                        cloud_mempool.Cloud_MemPool.append(task)
                        break

    def cloud_smartcontract_authenticator(self,target_task, replace_task,cloudnodes):

        result = True
        if target_task in self.un_authorized_tasks:
                result = False

        if result == False:
            return False

        return True


    def send_vms(self, receiver):
        """
        Sends VM information to a requesting fog node or other component.
        """
        receiver.receive_vms(vms=self.vms)

    def process_tasks(self):
        """
        Processes tasks assigned to the cloud's VMs and stores the results locally.
        """
        results = []
        for task in self.tasks:
            try:
                # Simulate task processing on a VM (random VM chosen)
                vm_id = random.randint(0, len(self.vms) - 1)
                result = eval(task[-2])  # Example computation
                results.append((task, result, f"Processed by VM {vm_id + 1}"))
            except Exception as e:
                results.append((task, f"Error: {e}", "Task failed"))
        self.local_storage.extend(results)
        self.tasks = []  # Clear tasks after processing
        return results
