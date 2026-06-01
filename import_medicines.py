import os
import csv
import django

#Django Environment Setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from medflowapp.models import Medicine

def seed_medicines():
    csv_file_path = "medicine_dataset.csv"
    if not os.path.exists(csv_file_path):
        print(f"Error: Could not find '{csv_file_path}' in the root folder.")
        return
    print("Analyzing and importing medicine records... Please wait.")

    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        medicine_instances=[]
        batch_size = 5000
        count =0

        for row in reader:
            med = Medicine(
                medicine_name=row['Name'].strip(),
                category = row['Category'].strip(),
                dosage_form=row['Dosage Form'].strip(),
                strength = row['Strength'].strip(),
                manufacturer=row['Manufacturer'].strip(),
                indication=row['Indication'].strip(),
                classification = row['Classification'].strip(),
                selling_price=15.50,
                stock_quantity=100,
                reorder_level=15
            )
            medicine_instances.append(med)

            #write out to DB whenever batch threshold is crossed
            if len(medicine_instances) >= batch_size:
                Medicine.objects.bulk_create(medicine_instances, ignore_conflicts=True)
                count += len(medicine_instances)
                print(f"Uploaded {count} records successfully...")
                medicine_instances = []
        # clear remaining items in queue
        if medicine_instances:
            Medicine.objects.bulk_create(medicine_instances, ignore_conflicts=True)
            count+=len(medicine_instances)
    print(f"\nCompleted! Successfully uploaded all {count} medicines into the database.")

if __name__ == "__main__":
    seed_medicines()    