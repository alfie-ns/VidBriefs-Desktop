# Change Ubuntu Static IP Address

Here's a step-by-step manual to change a static IP address in Ubuntu, based on the information provided in the video. 

## Step-by-Step Manual to Change a Static IP Address in Ubuntu

### Requirements:
- Ubuntu installed on a virtual machine (using VirtualBox as shown in the video)
- PuTTY installed on your Windows machine to access the Ubuntu virtual machine

### Steps:

1. **Open VirtualBox**: Start your Ubuntu virtual machine.

2. **Log into Ubuntu**: 
   - Use your credentials to access the system.
   - You can also log in via PuTTY using the IP address of your Ubuntu machine.

3. **Check Current IP Address**:
   - Enter the command:
     ```
     ip a
     ```
   - This command shows all network interfaces and their current configurations.

4. **Install Required Tools**:
   - If the `ifconfig` command is unavailable, install the net-tools package:
     ```bash
     sudo apt install net-tools
     ```

5. **Locate the Network Configuration File**:
   - Navigate to the `/etc/netplan` directory to find the configuration files:
     ```bash
     cd /etc/netplan
     ```

6. **Backup Configuration File**:
   - It’s a good practice to create a backup of the configuration file before modifying it:
     ```bash
     sudo cp 50-cloud-init.yaml 50-cloud-init.yaml.bak
     ```

7. **Edit the Configuration File**:
   - Open the configuration file in a text editor (e.g., `nano` or `vim`):
     ```bash
     sudo nano 50-cloud-init.yaml
     ```
   - Change the `dhcp` setting to `false` and set your desired static IP address, subnet mask, gateway, and DNS as follows:
     ```yaml
     network:
       version: 2
       ethernets:
         your_network_interface_name:
           addresses:
             - 192.168.1.90/24
           gateway4: 192.168.1.1
           nameservers:
             addresses:
               - 8.8.8.8
               - 8.8.4.4
     ```
   
8. **Save and Exit**: 
   - For `nano`, press `CTRL + X`, then `Y`, and hit `ENTER` to save changes.

9. **Create a Disable Configuration File (to prevent reverting)**:
   - Create another file to disable automatic network management:
     ```bash
     sudo touch /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg
     echo "network: {config: disabled}" | sudo tee -a /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg
     ```

10. **Apply the Changes**:
    - Apply the new configuration using:
      ```bash
      sudo netplan apply
      ```
    - Alternatively, you can use:
      ```bash
      sudo netplan try
      ```
    - This command allows you to test the configuration before applying it permanently.

11. **Verify Changes**:
    - Check if your IP address has changed:
      ```bash
      ip a
      ```
    - Ensure your new static IP is listed.

12. **Troubleshoot Errors**:
    - If you encounter any errors during the application, re-edit the configuration file, ensuring proper indentation and formatting, and try again.

13. **Reconnect Using PuTTY** (If disconnected):
    - Open a new PuTTY session using the new static IP address to verify the connection is successful.

14. **Keep Updated**:
    - Subscribe to channels or newsletters to stay informed on best practices for managing your server environments.

### Conclusion
By following these steps, you should successfully change a static IP address in your Ubuntu installation. Ensure to test connectivity after making changes and troubleshoot any issues that may arise following modifications to the network settings.

For more details, watch the video here: [Changing a Static IP Address in Ubuntu](https://youtu.be/n_KVqRscUzs?si=5DN8sjD3hl2BvqSU).

---

[Link to Video](https://youtu.be/n_KVqRscUzs?si=5DN8sjD3hl2BvqSU)