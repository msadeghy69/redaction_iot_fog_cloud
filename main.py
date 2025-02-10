from openpyxl.styles.builtins import output

import Fog
import cloud
import end_user
import miner
import blockchain
import random
import output
from math import ceil
import time
import modification
import new_consensus_module
import CloudBroker
from Fobsim_my_architecture.cloud import Cloud
import redaction.chameleon_hash as redaction1
data = modification.read_file("Sim_parameters.json")
list_of_end_users = []
fogNodes = []
cloudNodes = []
transactions_list = []
list_of_authorized_miners = []
blockchainFunction = 0
blockchainPlacement = 0
number_of_miner_neighbours = data["number_of_each_miner_neighbours"]
the_fog_miners_list = []

NumOfCloudNodes = data["NumOfCloudNodes"]  #add num cloud node *M
NumOfFogNodes = data["NumOfFogNodes"]
NumOfTaskPerUser = data["NumOfTaskPerUser"]
NumOfTaskPerFog = data["NumOfTaskPerFog"]
NumOfMiners = data["NumOfMiners"]
numOfTXperBlock = data["numOfTXperBlock"]
num_of_users_per_fog_node = data["num_of_users_per_fog_node"]
num_of_fogs_per_cloud_node = data["num_of_fogs_per_cloud_node"]
blockchain_functions = [1, 2, 3, 4]
blockchain_placement_options = ['1', '2']
expected_chain_length = ceil((num_of_users_per_fog_node * NumOfTaskPerUser * NumOfFogNodes) / numOfTXperBlock)
gossip_activated = data["Gossip_Activated"]
Automatic_PoA_miners_authorization = data["Automatic_PoA_miners_authorization?"]
Parallel_PoW_mining = data["Parallel_PoW_mining?"]
trans_delay = 0
cloud_trans_delay = 0 #add by ms
delay_between_cloud_nodes = data["delay_between_cloud_nodes"]
delay_between_fog_nodes = data["delay_between_fog_nodes"]
delay_between_end_users = data["delay_between_end_users"]





delay_between_iot_fogBroker = data['delay_between_iot_fogbroker']
delay_between_fogBroker_cloudBroker = data['delay_between_fogbroker_cloudbroker']
delay_between_cloudBroker_hosts = data['delay_between_cloudbroker_to_host']


poet_block_time = data['poet_block_time']
Asymmetric_key_length = data['Asymmetric_key_length']
number_of_DPoS_delegates = data['Num_of_DPoS_delegates']

enable_redaction=data['Isredaction']
redaction_algorithm=data['Reduction_Mechanism'] # 0 =sha256  / 1 = chameleon_hash_redaction

iot_attack_rates = data['attack_rates']  # Attack rates from 0% to 40% [0.0, 0.1, 0.2, 0.3, 0.4]

run_with_bc = data['run_with_bc']



user_informed = False
fog_informed = False
total_transactions_iot = 0
total_transactions_fog = 0
total_transactions = 0

def user_input():
    modification.initiate_files(gossip_activated)
    choose_functionality()
    choose_placement()


def choose_functionality():
    while True:
        output.choose_functionality()
        global blockchainFunction
        blockchainFunction = input()
        if int(blockchainFunction) in blockchain_functions:
            blockchainFunction = int(blockchainFunction)
            print("function is " ,blockchainFunction)
            break
        else:
            print("Input is incorrect, try again..!")


def choose_placement():
    #while True:
        #output.choose_placement()
        global blockchainPlacement
       # blockchainPlacement = input()
        blockchainPlacement = 1
        if str(blockchainPlacement) in blockchain_placement_options:
            blockchainPlacement = int(blockchainPlacement)

        else:
            print("Input is incorrect, try again..!")


def initiate_network():

    for count in range(NumOfCloudNodes):
        cloud_obj=cloud.Cloud(count + 1)
        cloudNodes.append(cloud_obj)


        for p in range(num_of_fogs_per_cloud_node):
            fog_node = Fog.Fog(cloud_obj.address * 100 + p , cloud_obj.address)
            fogNodes.append(fog_node)
            cloud_obj.connected_fog_nodes.add(fog_node)

            for e in range(num_of_users_per_fog_node):
                iot_user=end_user.User(fog_node.address * 100 +e, fog_node.address)
                list_of_end_users.append(iot_user)
                fog_node.list_of_connected_users.add(iot_user)

    cloud_broker = CloudBroker.CloudBroker(cloudNodes)
    output.users_and_fogs_and_clouds_are_up()
    if blockchainFunction == 4:
        output.GDPR_warning()
        while True:
            print("If you don't want other attributes to be added to end_users, input: done\n")
            new_attribute = input("If you want other attributes to be added to end_users, input them next:\n")
            if new_attribute == 'done':
                break
            else:
                for user in list_of_end_users:
                    user.identity_added_attributes[new_attribute] = ''
                output.user_identity_addition_reminder(len(list_of_end_users))
    for user in list_of_end_users:
        user.create_tasks(NumOfTaskPerUser, blockchainFunction, list_of_end_users)
    results = run_scenario_with_attack_rates(iot_attack_rates)  # add by ms
    for user in list_of_end_users:

        user.send_tasks(fogNodes)
        print("End_user " + str(user.addressParent) + "." + str(user.addressSelf) + " had sent its tasks to the fog layer")


    if run_with_bc:
        for fog in fogNodes: #add my ms
            fog.create_tasks(NumOfTaskPerFog, blockchainFunction, fogNodes) #add my ms
            fog.send_tasks_to_cloud(cloudNodes) #add my ms
            print("fog user " + str(fog.addressParent) + "." + str(fog.address) + " had sent its tasks to the cloud layer") #add my ms
    else :
        for fog in fogNodes:
            cloud_broker.distribute_tasks_least_loaded(fog.tasks, fog)
        cloud_broker.process_all_cloud_tasks()



    print("Cloud Nodes:")

    for cloud1 in cloudNodes:
        print(cloud1)

    # نمایش اطلاعات Fogها
    print("\nFog Nodes:")
    for fog in fogNodes:
        print(fog)

    # نمایش اطلاعات Userها
    print("\nUsers:")
    for user in list_of_end_users:
        print(user)

    return results

def initiate_fog_miners(x):


    if blockchainPlacement == 1:
        for i in range(NumOfFogNodes):
            the_fog_miners_list.append(miner.Miner((i+1) *10 + 1, x, gossip_activated))
    #if blockchainPlacement == 2:
    #    for i in range(NumOfMiners):
    #       the_fog_miners_list.append(miner.Miner(i + 1, trans_delay, gossip_activated))
    for entity in the_fog_miners_list:
        modification.write_file("temporary/" + entity.address + "_local_chain.json", {})
        miner_wallets_log_py = modification.read_file("temporary/miner_wallets_log.json")
        miner_wallets_log_py[str(entity.address)] = data['miners_initial_wallet_value']
        modification.rewrite_file("temporary/miner_wallets_log.json", miner_wallets_log_py)

    print('fog Miners have been initiated..')
    connect_miners(the_fog_miners_list)
    output.miners_are_up()
    print("pass fog")
    return the_fog_miners_list


def initiate_cloud_miners(y): #add by ms
    the_cloud_miners_list = []

    if blockchainPlacement == 1:
        for i in range(NumOfCloudNodes):
            the_cloud_miners_list.append(miner.Miner((i+1) * 10, y, gossip_activated))
        print("pass 1")
    #if blockchainPlacement == 2:
    #    for i in range(NumOfMiners):
    #        the_cloud_miners_list.append(miner.Miner(i + 1, trans_delay, gossip_activated))
    for entity in the_cloud_miners_list:
        print(the_cloud_miners_list[1],the_cloud_miners_list[2])
        print("pass 2")
        modification.write_file("temporary/" + entity.address + "_cloud_local_chain.json", {})
        print("pass 3")
        cloud_miner_wallets_log_py = modification.read_file("temporary/cloud_miner_wallets_log.json")
        print("pass 4")
        cloud_miner_wallets_log_py[str(entity.address)] = data['miners_initial_wallet_value']
        print("pass 5")
        modification.rewrite_file("temporary/cloud_miner_wallets_log.json", cloud_miner_wallets_log_py)
        print("pass 6")

    print('cloud Miners have been initiated..')
    print("pass 7")
    cloud_connect_miners(the_cloud_miners_list)
    print("pass 8")
    output.cloud_miners_are_up()
    print("pass 9")
    return the_cloud_miners_list

def define_fog_trans_delay(layer):
    transmission_delay = 0
    if layer == 1:
        transmission_delay = delay_between_fog_nodes


    if layer == 2:
        transmission_delay = delay_between_end_users
    return transmission_delay




def define_cloud_trans_delay(layer): #add by ms
    transmission_delay = 0
    if layer == 1:

        transmission_delay = delay_between_cloud_nodes

    if layer == 2:
        transmission_delay = delay_between_end_users
    return transmission_delay


def define_trans_delay(): #add by ms
    transmission_delay = delay_between_iot_fogBroker+delay_between_fogBroker_cloudBroker+delay_between_cloudBroker_hosts

    time.sleep(delay_between_iot_fogBroker+delay_between_fogBroker_cloudBroker+delay_between_cloudBroker_hosts)
    return transmission_delay

def connect_miners(miners_list):
    print("fog Miners will be connected in a P2P fashion now. Hold on...")
    bridges = set()
    all_components = create_components(miners_list)
    for comp in all_components:
        bridge = random.choice(tuple(comp))
        bridges.add(bridge)
    bridging(bridges, miners_list)

def cloud_connect_miners(miners_list):
    print(" cloud Miners will be connected in a P2P fashion now. Hold on...")
    bridges = set()
    all_components = create_components(miners_list)
    for comp in all_components:
        bridge = random.choice(tuple(comp))
        bridges.add(bridge)
    bridging(bridges, miners_list)

def bridging(bridges, miners_list):
    while len(bridges) != 1:
        bridge = random.choice(tuple(bridges))
        other_bridge = random.choice(tuple(bridges))
        same_bridge = True
        while same_bridge:
            other_bridge = random.choice(tuple(bridges))
            if other_bridge != bridge:
                same_bridge = False
        for entity in miners_list:
            if entity.address == bridge:
                entity.neighbours.add(other_bridge)
            if entity.address == other_bridge:
                entity.neighbours.add(bridge)
        bridges.remove(bridge)


def create_components(miners_list):
    all_components = set()
    for entity in miners_list:
        component = set()
        while len(entity.neighbours) < number_of_miner_neighbours:
            neighbour = random.choice(miners_list).address
            if neighbour != entity.address:
                entity.neighbours.add(neighbour)
                component.add(neighbour)
                for entity_2 in miners_list:
                    if entity_2.address == neighbour:
                        entity_2.neighbours.add(entity.address)
                        component.add(entity.address)
                        break
        if component:
            all_components.add(tuple(component))
    return all_components


def give_miners_authorization(the_miners_list, the_type_of_consensus):
    if the_type_of_consensus == 1:
        wanted, float_portion = output.AI_assisted_mining_wanted()
        if wanted:
            num_of_miners_requested_to_use_AI = ceil(float_portion * len(the_miners_list))
            num_of_miners_instructed_to_use_AI = 0
            while num_of_miners_instructed_to_use_AI < num_of_miners_requested_to_use_AI:
                random_miner = random.choice(the_miners_list)
                if not random_miner.adversary:
                    random_miner.adversary = True
                    num_of_miners_instructed_to_use_AI += 1
            print(str(num_of_miners_instructed_to_use_AI) + ' miners were successfully instructed to use AI.')
        return wanted
    if the_type_of_consensus == 3:
        # automated approach:
        if Automatic_PoA_miners_authorization:
            for i in range(len(the_miners_list)):
                the_miners_list[i].isAuthorized = True
                list_of_authorized_miners.append(the_miners_list[i])
        else:
            # user input approach:
            output.authorization_trigger(blockchainPlacement, NumOfFogNodes, NumOfMiners)
            while True:
                authorized_miner = input()
                if authorized_miner == "done":
                    break
                else:
                    for node in the_miners_list:
                        if node.address == "Miner_" + authorized_miner:
                            node.isAuthorized = True
                            list_of_authorized_miners.append(node)
    return None


def initiate_genesis_block(AI_wanted):
    genesis_transactions = ["genesis_block"]
    for i in range(len(miner_list)):
        genesis_transactions.append(miner_list[i].address)
    genesis_block = new_consensus_module.generate_new_block(genesis_transactions, 'The Network', 0, type_of_consensus, AI_wanted, False)
    output.block_info(genesis_block, type_of_consensus)
    print("pass 1")
    for elem in miner_list:
        elem.receive_new_block(genesis_block, type_of_consensus, miner_list, blockchainFunction, expected_chain_length)
    print("pass 2")
    output.genesis_block_generation()
    print("pass 3")


def initiate_cloud_genesis_block(AI_wanted):
    print("pass 4")
    genesis_transactions = ["genesis_block"]
    print("pass 5")
    for i in range(len(cloud_miner_list)):
        genesis_transactions.append(cloud_miner_list[i].address)
    print("pass 6")
    genesis_block = new_consensus_module.generate_new_block(genesis_transactions, 'The Network', 0, type_of_consensus, AI_wanted, False)
    print("pass 7")
    output.block_info(genesis_block, type_of_consensus)
    print("pass 8")
    for elem in cloud_miner_list:
        print("pass 9")
        elem.receive_cloud_new_block(genesis_block, type_of_consensus, cloud_miner_list, blockchainFunction, expected_chain_length)
    print("pass 10")
    print(type(cloud_miner_list))
    for elem in cloud_miner_list:
        print("Checking miner:", elem.address)


    print("pass 11")
    output.genesis_block_generation()
    print("pass 11")

def send_tasks_to_BC():
    global user_informed
    for node in fogNodes:
        node.send_tasks_to_BC(user_informed)
        if not user_informed:
            user_informed = True

def modification_tasks(algo , modify_type,fogNodes , cloudNodes ): #add by ms


        selected_user = list_of_end_users[0]
        a=selected_user.modification_tasks_act(algo, modify_type, fogNodes, cloudNodes, list_of_end_users)
        return a






def send_cloud_tasks_to_BC():
    global fog_informed
    for node in cloudNodes:
        node.send_cloud_tasks_to_BC(fog_informed) #add by ms
        if not fog_informed:
            fog_informed = True

def store_fog_data():
    for node in fogNodes:
        log = open('temporary/Fog_node_'+str(node.address)+'.txt', 'w')
        log.write(str(node.local_storage))


def store_cloud_data():#add by ms
    for node in cloudNodes:
        log = open('temporary/cloud_node_'+str(node.address)+'.txt', 'w')
        log.write(str(node.local_storage))

def inform_miners_of_users_wallets():
    if blockchainFunction == 3:
        user_wallets = {}
        for user in list_of_end_users:
            wallet_info = {'parent': user.addressParent,
                           'self': user.addressSelf,
                           'wallet_value': user.wallet}
            user_wallets[str(user.addressParent) + '.' + str(user.addressSelf)] = wallet_info
        for i in range(len(miner_list)):
            modification.rewrite_file(str("temporary/" + miner_list[i].address + "_users_wallets.json"), user_wallets)


##1
def set_adversaries(users, attack_rate):

    num_adversaries = int(len(users) * attack_rate)
    adversaries = random.sample(users, num_adversaries)
    for user in adversaries:
        user.adversary = True
    print(f"Adversaries Set: {len(adversaries)} out of {len(users)} IoT devices")
    return adversaries

def simulate_and_evaluate():

    # Placeholder logic for simulating and evaluating
    print("Simulating tasks...")
    success_rate = random.uniform(50, 95)  # Example placeholder value
    return success_rate



##2- Add a function in main.py to iterate over attack rates:
def run_scenario_with_attack_rates(rate):

    #reset adversary to false
    for u in list_of_end_users:
        u.adversary = False

    adversaries = set_adversaries(list_of_end_users, rate)

    # Simulate and evaluate
    success_rate = simulate_and_evaluate()

    results=f"Attack Rate: {int(rate * 100)}% - Success Rate: {success_rate} -adversaries :{len(adversaries)} "
    return results


def calculate_tamper_resistance(num_iot_devices, num_fog_devices, attack_rate):
    """
    Calculate tamper resistance based on IoT devices, fog devices, and attack rate.

    Parameters:
    - num_iot_devices: Number of IoT devices in the scenario.
    - num_fog_devices: Number of fog devices in the scenario.
    - attack_rate: Proportion of malicious IoT devices (e.g., 0.3 for 30%).

    Returns:
    - Tamper resistance metric (float).
    """
    # Define base probabilities for failures
    base_P_cs_fail = 0.01  # Cryptographic failure (e.g., hash collision)
    base_P_cons_fail = 0.05  # Consensus mechanism failure (e.g., 51% attack)
    base_P_acs_fail = 0.02  # Access control failure (e.g., unauthorized access)

    # Adjust probabilities based on the number of devices and attack rate
    P_cs_fail = base_P_cs_fail * (1 + attack_rate)  # More attacks increase cryptographic failure likelihood
    P_cons_fail = base_P_cons_fail * (num_fog_devices / 10)  # Scale more aggressively
    P_acs_fail = base_P_acs_fail * (num_iot_devices / 30)  # Increase IoT effect

    print(P_cs_fail)
    print(P_cons_fail)
    print(P_acs_fail)

    # Calculate probability of unauthorized changes
    P_unauthorized_change = (P_cs_fail + P_cons_fail + P_acs_fail) / 3
    print(P_unauthorized_change)


    # Calculate Tamper Resistance
    tamper_resistance = 1 - P_unauthorized_change
    return tamper_resistance

if __name__ == '__main__':
    if run_with_bc :
        user_input()
        time_start = time.time()
        results=initiate_network()
        type_of_consensus = new_consensus_module.choose_consensus()
        trans_delay = define_fog_trans_delay(blockchainPlacement)
        cloud_trans_delay =define_cloud_trans_delay(blockchainPlacement) #add by ms
        miner_list = initiate_fog_miners(trans_delay)
        cloud_miner_list = initiate_cloud_miners(cloud_trans_delay) #add by ms

        AI_assisted_mining_wanted = give_miners_authorization(miner_list, type_of_consensus)
        AI_assisted_cloud_mining_wanted = give_miners_authorization(cloud_miner_list, type_of_consensus) #add by ms

        inform_miners_of_users_wallets()

        blockchain.stake(miner_list, type_of_consensus)

        initiate_genesis_block(AI_assisted_mining_wanted)
        initiate_cloud_genesis_block(AI_assisted_cloud_mining_wanted)



        send_tasks_to_BC()
        if enable_redaction:
            algo , modify_type = output.redaction_input() #(1) Delete   (2) Modify /// #(1) Chameleon Hash (2) Voting-Based (3) Mutation-Based
            received_task=modification_tasks(algo , modify_type,fogNodes , cloudNodes) #add by ms
            for item in cloudNodes:
                print("item is ", item.tasks)
                print(received_task)
                item.tasks.append(received_task)
                print("item is ", item.tasks)
                break

        redaction_algorithm=0
        send_cloud_tasks_to_BC() #add by ms


        if blockchainFunction == 2:
            expected_chain_length = ceil((num_of_users_per_fog_node * NumOfTaskPerUser * NumOfFogNodes))
        new_consensus_module.miners_trigger(miner_list, type_of_consensus, expected_chain_length, Parallel_PoW_mining,
                                            numOfTXperBlock, blockchainFunction, poet_block_time, Asymmetric_key_length,
                                            number_of_DPoS_delegates, AI_assisted_mining_wanted)

        blockchain.award_winning_miners(len(miner_list), miner_list)
        blockchain.cloud_award_winning_miners(len(cloud_miner_list), cloud_miner_list)

        blockchain.fork_analysis(miner_list)
        blockchain.cloud_fork_analysis(cloud_miner_list)


        output.finish()

        store_fog_data()
        store_cloud_data()
        #### calculate throughput #add my ms
        for user in list_of_end_users:#add my ms

            total_transactions_iot+=len(user.tasks)

        for fog in fogNodes: #add my ms

            total_transactions_fog+=len(fog.tasks) #add my ms

        total_transactions=total_transactions_iot + total_transactions_fog

        ####


        latency = time.time() - time_start
        throughput = total_transactions / latency

        print("Latency = " + str(latency) + " seconds \n")

        print("total_transactions = " + str(total_transactions) + "\n")

        print("throughput = " + str(throughput) + "  Transactions per Second (TPS) \n")
        print(results + "\n")

        TR = calculate_tamper_resistance(num_of_users_per_fog_node * NumOfFogNodes , NumOfFogNodes, iot_attack_rates)
        print(f"Attack Rate: {int(iot_attack_rates * 100)}%, Tamper Resistance: {TR:.6f}")


    else :

        time_start = time.time()
        blockchainFunction=1
        results = initiate_network()

        trans_delay = define_trans_delay()





        store_fog_data()
        store_cloud_data()
        #### calculate throughput #add my ms
        for user in list_of_end_users:  # add my ms

            total_transactions_iot += len(user.tasks)



        total_transactions = total_transactions_iot

        ####

        latency = time.time() - time_start
        throughput = total_transactions / latency

        print("Latency = " + str(latency) + " seconds \n")

        print("total_transactions = " + str(total_transactions) + "\n")

        print("throughput = " + str(throughput) + "  Transactions per Second (TPS) \n")
        print(results + "\n")

        TR = calculate_tamper_resistance(num_of_users_per_fog_node * NumOfFogNodes, NumOfFogNodes, iot_attack_rates)
        print(f"Attack Rate: {int(iot_attack_rates * 100)}%, Tamper Resistance: {TR:.6f}")






