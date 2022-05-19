import pyodbc
import time
import paramiko
import datetime
import schedule
import os
import getpass

def backup():
    # AW deklaracje
    currentDateTime = datetime.datetime.now()
    remotePath = "/var/opt/mssql/data/" + fileName #Set your path for backups defined for your SQL SERVER installed on UBUNTU
    localPath = "C:/BACKUP/" + fileName #Set path for Windows machine to store your database backup
    sudoCommand = "sudo -S chmod -R 777 /var/opt/mssql"
    RemoveFileCommand = "rm " + remotePath
    remoteUser = input("UBUNTU User: ")
    remotePass = getpass.getpass(prompt = "UBUNTU password: ")
    server = input("Server ip: ")
    database = input("Database name: ")
    fileName = currentDateTime.strftime(database + "_%Y-%m-%d_%H-%M.bak")
    username = input("SQL User: ")
    password = getpass.getpass(prompt = "SQL password: ")
    
    dbConnectionString = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password

    os.system('cls')
    print("BACKUP START")

    # AW Łączenie z bazą
    print("Initializating database connection")
    cnxn = pyodbc.connect(dbConnectionString)
    cursor = cnxn.cursor()

    # AW Tworzenie backup na dysku lokalnym ubuntu
    print("Creating backup")
    query = ("""BACKUP DATABASE MEDOK_CS_WAW_MCS TO DISK = N'""" + fileName + """';""")
    cnxn.autocommit = True
    msg = cursor.execute(query)
    cursor.commit()
    time.sleep(5)

    # AW Nadanie plikom nowych uprawnień
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, username=remoteUser, password=remotePass)
    stdin, stdout, stderr = client.exec_command(sudoCommand)
    time.sleep(1)
    stdin.write(remotePass + '\n')
    time.sleep(1)
    stdin.flush()
    client.close()

    # AW kopiowane pliku
    print("copying files")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, username=remoteUser, password=remotePass)
    sftp_client = client.open_sftp()
    sftp_client.get(remotePath, localpath=localPath)
    sftp_client.close()
    client.close()
    time.sleep(1)
    print("backup in " + localPath)

    # AW usuwanie plików
    print("removing files")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, username=remoteUser, password=remotePass)
    stdin, stdout, stderr = client.exec_command(RemoveFileCommand)
    stdin.flush()
    client.close()
    
    
backup()
