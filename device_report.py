import re
import paramiko
import csv

with open("list_device.txt", "r") as f:
    load_device = f.read().splitlines()
    f.close()

user = "admin"
passw = "C!sc0"
cmd = "show version"

device_list = []

for i in load_device:
    try:
        #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        device = []
        print("Trying to connet on device: ", i)
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=i, username=user, password=passw, timeout=20)

        #ssh = ssh_client.invoke_shell()
        stdin, stdout, stderr = ssh_client.exec_command(cmd, timeout=10)

        result = stdout.read()
        result_reg = re.search( r"\S+\suptime.*", result)
        device.append(result_reg.group(0).split()[0])

        result_reg = re.search( r"Model number.+.*", result)
        device.append(result_reg.group(0).split()[-1])
        result_reg = re.search( r"System image file is.+", result)
        device.append(result_reg.group(0).split('"')[1].strip("flash:/"))
        result_reg = re.search( r"System serial number.+", result)
        device.append(result_reg.group(0).split()[-1])
        result_reg = re.search( r"Version.+", result)
        device.append(result_reg.group(0).split()[1].strip('"'))

        device_list.append(device)
        print("Device: " + i + " is OK")
        ssh_client.close()
    except socket.error as e:
        print("Connection timeout to IP ", i)
        ssh_client.close()
        pass
    except paramiko.ssh_exception.AuthenticationException as e:
        print("Authentication Failed to IP ", i)
        ssh_client.close()
        pass
    except AttributeError as e:
        print(i, " Probably is not a Cisco device.")
        ssh_client.close()
        pass
    except paramiko.ssh_exception.SSHException as e:
        print("Connection reset to IP ", i)
        ssh_client.close()
        pass

with open("report.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(device_list)

print("Device List: ", device_list)
