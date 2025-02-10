import random


class CloudBroker:
    def __init__(self, cloud_nodes):
        """
        Initializes the Cloud Broker with a list of available cloud nodes.
        """
        self.cloud_nodes = cloud_nodes  # لیست دیتا سنترهای کلود

    def distribute_tasks(self, tasks, sender):
        """
        Distributes tasks from a fog node to an appropriate cloud data center.
        """
        if not self.cloud_nodes:
            print("No cloud nodes available!")
            return

        # انتخاب دیتا سنتر به روش تصادفی
        selected_cloud = random.choice(self.cloud_nodes)
        selected_cloud.receive_tasks(tasks, sender)
        print(f"Broker sent {len(tasks)} tasks from Fog {sender.address} to Cloud {selected_cloud.address}")

    def distribute_tasks_least_loaded(self, tasks, sender):
        """
        Distributes tasks to the least loaded cloud data center.
        """
        if not self.cloud_nodes:
            print("No cloud nodes available!")
            return

        # انتخاب دیتا سنتر با کمترین وظایف در صف پردازش
        least_loaded_cloud = min(self.cloud_nodes, key=lambda c: len(c.tasks))
        least_loaded_cloud.receive_tasks(tasks, sender)
        print(f"Broker sent {len(tasks)} tasks from Fog {sender.address} to Cloud {least_loaded_cloud.address}")

    def process_all_cloud_tasks(self):
        """
        Processes tasks on all connected cloud data centers.
        """
        for cloud in self.cloud_nodes:
            results = cloud.process_tasks()
            print(f"Cloud {cloud.address} processed {len(results)} tasks.")
