import time  # اضافه کردن کتابخانه time

if __name__ == '__main__':
    # ثبت زمان شروع شبیه‌سازی
    time_start = time.time()

    # شمارش تعداد تراکنش‌های پردازش‌شده
    total_transactions_fog = 0
    total_transactions_blockchain = 0
    total_transactions_cloud = 0

    # اجرای شبیه‌سازی
    user_input()
    initiate_network()

    # ثبت تراکنش‌های ارسال‌شده به لایه Fog
    for fog_node in fogNodes:
        total_transactions_fog += len(fog_node.tasks)

    type_of_consensus = new_consensus_module.choose_consensus()
    trans_delay = define_trans_delay(blockchainPlacement)
    miner_list = initiate_miners()
    AI_assisted_mining_wanted = give_miners_authorization(miner_list, type_of_consensus)
    inform_miners_of_users_wallets()
    blockchain.stake(miner_list, type_of_consensus)
    initiate_genesis_block(AI_assisted_mining_wanted)
    send_tasks_to_BC()


    for miner in miner_list:
        total_transactions_blockchain += len(miner.local_mempool)


    if hasattr(cloud, 'vms'):
        for vm in cloud.vms:
            total_transactions_cloud += len(vm)


    if blockchainFunction == 2:
        expected_chain_length = ceil((num_of_users_per_fog_node * NumOfTaskPerUser * NumOfFogNodes))
    new_consensus_module.miners_trigger(
        miner_list, type_of_consensus, expected_chain_length, Parallel_PoW_mining,
        numOfTXperBlock, blockchainFunction, poet_block_time, Asymmetric_key_length,
        number_of_DPoS_delegates, AI_assisted_mining_wanted
    )
    blockchain.award_winning_miners(len(miner_list), miner_list)
    blockchain.fork_analysis(miner_list)
    output.finish()
    store_fog_data()

    # ثبت زمان پایان شبیه‌سازی
    elapsed_time = time.time() - time_start
    print(f"Elapsed time = {elapsed_time} seconds")

    # محاسبه Throughput
    total_transactions = total_transactions_fog + total_transactions_blockchain + total_transactions_cloud
    throughput = total_transactions / elapsed_time
    print(f"Throughput = {throughput:.2f} transactions per second")
    print(f"Fog Transactions: {total_transactions_fog}")
    print(f"Blockchain Transactions: {total_transactions_blockchain}")
    print(f"Cloud Transactions: {total_transactions_cloud}")
