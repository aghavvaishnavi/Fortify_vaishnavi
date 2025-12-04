# This program runs on Windows.
# It detects USB insert and remove events,
# logs running processes when a USB event happens,
# logs system usage every 5 seconds,
# sends an email alert on USB insertion,
# and stores everything in ONE single log file.

import psutil                     # For CPU, memory, disk, network and drive info
import time                       # For delays (sleep)
import threading                  # To run USB monitor and system monitor together
import smtplib                    # For sending emails
from email.mime.text import MIMEText   # To format email body
from datetime import datetime     # To get current date and time


# Name of the single log file
LOG_FILE = "system_monitor.log"


# This function writes any message into the log file
def write_log(text):
    # Open the file in append mode so old data is not erased
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(text + "\n")


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SENDER_EMAIL = "vaishnaviaghav1206@gmail.com"  #my gmail
SENDER_PASSWORD = "jhsshgfnviuoweut"     #app password
RECEIVER_EMAIL = "vaishaghav9175@gmail.com" # Where the alert email should go


# This function sends an email when a USB is inserted
def send_email_alert(device_name):
    subject = "USB Device Inserted Alert"

    body = f"""
A USB device was inserted.

Device: {device_name}
Time  : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

    # Create email message
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    try:
        # Connect to Gmail server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()                      # Secure the connection
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()

        write_log("Email alert sent successfully")

    except Exception as error:
        write_log("Email failed to send: " + str(error))


# This function logs all running processes when a USB event happens
def log_process_snapshot():
    write_log("Process Snapshot")
    write_log("PID        NAME                CPU%      MEM%")

    # Loop through every running process
    for process in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            pid = process.info['pid']
            name = process.info['name']
            cpu = process.info['cpu_percent']
            memory = process.info['memory_percent']

            # Write process details to log file
            write_log(f"{pid:<10}{name:<20}{cpu:<10.2f}{memory:.2f}")

        except:
            # Ignore processes that close suddenly or deny access
            pass


# This function detects ONLY real removable USB drives
def monitor_usb():
    # This will store the currently connected USB drives
    connected = set()

    write_log("USB polling started")

    while True:
        time.sleep(2)     # Check every 2 seconds

        current = set()   # This will store currently detected USB drives

        # Get all disk partitions from Windows
        partitions = psutil.disk_partitions(all=True)

        for part in partitions:
            # Only picks removable drives (real USB)
            if "removable" in part.opts.lower():
                current.add(part.device)

        # Detect newly inserted USB drives
        new_drives = current - connected
        for drive in new_drives:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            write_log(f"[{current_time}] USB INSERTED: {drive}")
            print("USB INSERTED:", drive)

            log_process_snapshot()
            send_email_alert(drive)

        # Detect removed USB drives
        removed_drives = connected - current
        for drive in removed_drives:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            write_log(f"[{current_time}] USB REMOVED: {drive}")
            print("USB REMOVED:", drive)

            log_process_snapshot()

        # Update the connected USB list
        connected = current


# This function logs system usage every 5 seconds
def monitor_system_resources():
    previous_disk = psutil.disk_io_counters()
    previous_net = psutil.net_io_counters()

    while True:
        time.sleep(5)     # Log every 5 seconds

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent

        current_disk = psutil.disk_io_counters()
        current_net = psutil.net_io_counters()

        # Calculate disk I/O in MB/s
        disk_io = (
            current_disk.read_bytes + current_disk.write_bytes -
            previous_disk.read_bytes - previous_disk.write_bytes
        ) / (1024 * 1024)

        # Calculate network I/O in MB/s
        net_io = (
            current_net.bytes_sent + current_net.bytes_recv -
            previous_net.bytes_sent - previous_net.bytes_recv
        ) / (1024 * 1024)

        previous_disk = current_disk
        previous_net = current_net

        # Write system stats to the single log file
        write_log(f"[{current_time}] SYSTEM STATS")
        write_log(f"CPU Usage: {cpu}%")
        write_log(f"Memory Usage: {memory}%")
        write_log(f"Disk I/O: {disk_io:.2f} MB/s")
        write_log(f"Network I/O: {net_io:.2f} MB/s")


# This is the main function that starts both monitoring tasks
def main():
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    write_log("Monitor started at " + start_time)

    # One thread for USB monitoring
    usb_thread = threading.Thread(target=monitor_usb)

    # One thread for system resource monitoring
    system_thread = threading.Thread(target=monitor_system_resources)

    # Start both threads
    usb_thread.start()
    system_thread.start()

    # Keep both threads running forever
    usb_thread.join()
    system_thread.join()


# Program execution starts here
if __name__ == "__main__":
    main()
