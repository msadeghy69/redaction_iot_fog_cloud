import random
from random import randrange
import redaction.chameleon_hash as redaction1
import output
import modification
#from Fobsim_my_architecture.main import list_of_end_users
import main as m
import encryption_module as em
data = modification.read_file("Sim_parameters.json")
import json


class User:
    def __init__(self, address, parent):
        self.addressParent = parent
        self.addressSelf = address
        self.adversary=False
        self.tasks = []
        self.modification_tasks = [] #add by ms
        self.identity_added_attributes = {}
        self.wallet = data["Max_enduser_payment"] * data["NumOfTaskPerUser"]
        self.STOR_PLC = data["STOR_PLC(0=in the Fog,1=in the BC)"]
        self.target_task = ""
        self.replace_task = ""

    def __str__(self):
        tasks_details = [str(task) for task in self.tasks]

        return (f"User Address: {self.addressSelf}, Parent Fog: {self.addressParent}, "
                f"Tasks: {tasks_details}, Identity Attributes: {self.identity_added_attributes}, "
                f"Wallet: {self.wallet}, STOR_PLC: {self.STOR_PLC}")

    def create_tasks(self, num_of_task_per_user, blockchain_function, list_of_end_users):
        if blockchain_function == 1:
            self.__apply_first_functionality(num_of_task_per_user, blockchain_function)
        if blockchain_function == 2:
            self.__apply_second_functionality(num_of_task_per_user, blockchain_function)
        if blockchain_function == 3:
            self.__apply_third_functionality(num_of_task_per_user, list_of_end_users, blockchain_function)
        if blockchain_function == 4:
            self.__apply_forth_functionality(blockchain_function,num_of_task_per_user)

    def send_tasks(self, list_of_fog_nodes): #add by ms
        for obj in list_of_fog_nodes:
            if obj.address == self.addressParent:
                obj.receive_tasks(self.tasks, self.addressSelf)
                break

    def modification_tasks_act(self, redaction_algorithm, modification_type, fognodes , cloudnodes,list_end_user): #add by ms

            #(1) Delete   (2) Modify
            #(1) Chameleon Hash   (2) Voting-Based  (3) Mutation-Based

            self.target_task = random.choice(self.tasks)
            self.replace_task = random.choice(self.tasks)

            deleted_task = [str(self.target_task) +"d"]
            replaced_task = [str(self.replace_task)+"mto"+str(self.target_task)]

            auth=True
            for obj in fognodes:
                if obj.address == self.addressParent:
                    auth = obj.fog_smartcontract_authenticator(self.target_task,self.replace_task,fognodes,cloudnodes, self.addressSelf,self.addressParent,list_end_user)
                    break


            if auth == True :

                if redaction_algorithm == 1 :
                    if modification_type == 1 :


                        for miner in m.the_fog_miners_list:
                            local_chain_path = f"temporary/{miner.address}_local_chain.json"
                            local_chain = modification.read_file(local_chain_path)

                            block_found = False  # نشان می‌دهد که بلاک دارای تراکنش پیدا شده یا خیر

                            for block_key, block in local_chain.items():
                                # جستجوی تراکنش در بلاک
                                if self.target_task in block["Body"]["transactions"]:
                                    block_found = True
                                    print(f"Target transaction found in block {block_key} for miner {miner.address}")
                                    self.replace_task = ""
                                    old_block_message = json.dumps(block["Body"], sort_keys=True)
                                    # تغییرات در بلاک
                                    block["Body"]["transactions"] = [
                                        self.replace_task if tx == self.target_task else tx for tx in
                                        block["Body"]["transactions"]
                                    ]
                                    block_key_unique = hash(old_block_message)  # یا هر روش دیگری برای تولید کلید
                                    old_r = em.data_r_dict[block_key_unique]

                                    new_block_message = json.dumps(block["Body"], sort_keys=True)

                                    new_r = em.ch.forge(
                                        old_block_message,  # The original hash
                                        new_block_message,  # The new block content
                                        old_r
                                    )
                                    new_hash, _ = em.ch.hash(new_block_message,  new_r)
                                    block["Header"]["hash"] = new_hash
                                    local_chain[block_key] = block
                                    modification.rewrite_file(local_chain_path, local_chain)

                                    print(f"Block {block_key} updated for miner {miner.address}")
                                    break  # پس از پیدا کردن بلاک، ادامه نمی‌دهیم
                        return deleted_task



                    elif modification_type == 2:
                        for miner in m.the_fog_miners_list:
                            local_chain_path = f"temporary/{miner.address}_local_chain.json"
                            local_chain = modification.read_file(local_chain_path)

                            block_found = False  # نشان می‌دهد که بلاک دارای تراکنش پیدا شده یا خیر

                            for block_key, block in local_chain.items():
                                # جستجوی تراکنش در بلاک
                                if self.target_task in block["Body"]["transactions"]:
                                    block_found = True
                                    print(f"Target transaction found in block {block_key} for miner {miner.address}")

                                    old_block_message = json.dumps(block["Body"], sort_keys=True)
                                    # تغییرات در بلاک
                                    block["Body"]["transactions"] = [
                                        self.replace_task if tx == self.target_task else tx for tx in
                                        block["Body"]["transactions"]
                                    ]
                                    block_key_unique = hash(old_block_message)  # یا هر روش دیگری برای تولید کلید
                                    old_r = em.data_r_dict[block_key_unique]

                                    new_block_message = json.dumps(block["Body"], sort_keys=True)

                                    new_r = em.ch.forge(
                                        old_block_message,  # The original hash
                                        new_block_message,  # The new block content
                                        old_r
                                    )
                                    new_hash, _ = em.ch.hash(new_block_message,  new_r)
                                    block["Header"]["hash"] = new_hash
                                    local_chain[block_key] = block
                                    modification.rewrite_file(local_chain_path, local_chain)

                                    print(f"Block {block_key} updated for miner {miner.address}")
                                    break  # پس از پیدا کردن بلاک، ادامه نمی‌دهیم

                        return replaced_task
                        #print(f"Cloud nodes: {m.cloudNodes}")
                        #for node in m.cloudNodes:
                         #   print("task is ",node.tasks)
                       # m.cloudNodes[1].tasks.append(replaced_task)




    def send_modification_tasks(self, list_of_fog_nodes,list_of_cloud_nodes): #add by ms
        for obj in list_of_fog_nodes:
            if obj.address == self.addressParent:
                obj.receive_modification_tasks(self.modification_tasks, self.addressSelf)
                break

    def __apply_first_functionality(self, num_of_task_per_user, blockchain_function):
        if self.adversary:
            print(f"Adversary {self.addressSelf} sending malicious tasks...")
            for task_number in range(num_of_task_per_user):
                self.tasks.append(["M{}".format(random.randint(0, 1000000)), blockchain_function])
        else :
            for task_number in range(num_of_task_per_user):
                self.tasks.append([random.randint(0, 1000000), blockchain_function])
        output.txs_success(num_of_task_per_user, self.addressParent, self.addressSelf)

    def __apply_second_functionality(self, num_of_task_per_user, blockchain_function):
        operations = ['+', '-', '*', '/']
        if self.adversary:
            print(f"Adversary {self.addressSelf} sending malicious tasks...")
            for task_number in range(num_of_task_per_user):
                operation = random.choice(operations)
                random_computational_task = str(randrange(1000000)) + operation + str(randrange(1000000))
                self.tasks.append(["M",self.addressParent, self.addressSelf, random_computational_task, blockchain_function])

        else :
            for task_number in range(num_of_task_per_user):
                operation = random.choice(operations)
                random_computational_task = str(randrange(1000000)) + operation + str(randrange(1000000))
                self.tasks.append([self.addressParent, self.addressSelf, random_computational_task, blockchain_function])


    def __apply_third_functionality(self, num_of_task_per_user, list_of_end_users, blockchain_function):
        if self.adversary:
            for task_number in range(num_of_task_per_user):
                print(f"Adversary {self.addressSelf} sending malicious tasks...")
                payment = randrange(round(data["Max_enduser_payment"], 0))
                receiver = random.choice(list_of_end_users)
                receiver_parent_address = receiver.addressParent
                receiver_individual_address = receiver.addressSelf
                proposed_transaction = ["M",payment, self.addressParent, self.addressSelf, receiver_parent_address,
                                        receiver_individual_address, blockchain_function]
                self.tasks.append(proposed_transaction)
        else:
            for task_number in range(num_of_task_per_user):
                payment = randrange(round(data["Max_enduser_payment"], 0))
                receiver = random.choice(list_of_end_users)
                receiver_parent_address = receiver.addressParent
                receiver_individual_address = receiver.addressSelf
                proposed_transaction = [payment, self.addressParent, self.addressSelf, receiver_parent_address,
                                        receiver_individual_address, blockchain_function]
                self.tasks.append(proposed_transaction)


    def __apply_forth_functionality(self, blockchain_function,num_of_task_per_user):

        if self.adversary:
            add_new_attributes(self)
            proposed_transaction = ["M",self.addressParent, self.addressSelf, self.identity_added_attributes,
                                    blockchain_function]
            self.tasks.append(proposed_transaction)
        else :
            add_new_attributes(self)
            proposed_transaction = [self.addressParent, self.addressSelf, self.identity_added_attributes,
                                    blockchain_function]
            self.tasks.append(proposed_transaction)


def add_new_attributes(user):
    for key in user.identity_added_attributes:
        user.identity_added_attributes[key] = input(
            str(user.addressParent) + "." + str(user.addressSelf) + ": " + key + ">> ")
