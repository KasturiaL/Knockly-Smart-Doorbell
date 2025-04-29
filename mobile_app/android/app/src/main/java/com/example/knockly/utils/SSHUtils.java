package com.example.knockly.utils;

import static android.content.ContentValues.TAG;

import android.content.Context;
import android.net.wifi.WifiManager;
import android.text.format.Formatter;
import android.util.Log;

import com.jcraft.jsch.Channel;
import com.jcraft.jsch.ChannelExec;
import com.jcraft.jsch.JSch;
import com.jcraft.jsch.JSchException;
import com.jcraft.jsch.Session;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.Inet4Address;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.NetworkInterface;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;

public class SSHUtils {

    public static List<String> ping(String subnetIP) {
        List<String> hosts = new ArrayList<>();

        try
        {
            int timeout=150;
            for (int i=1;i<255;i++)
            {
                String host=subnetIP + "." + i;
                if (InetAddress.getByName(host).isReachable(timeout) || isReachable(host,80,timeout))
                {
                    Log.d(TAG, "ping() :: "+host + " is reachable");
                    hosts.add(host);
                }
            }
        }
        catch (UnknownHostException e)
        {
            Log.d(TAG, "ping() :: UnknownHostException e : "+e);
            e.printStackTrace();
        }
        catch (IOException e)
        {
            Log.d(TAG, "ping() :: IOException e : "+e);
            e.printStackTrace();
        }

        return hosts;
    }

    private static boolean isReachable(String addr, int openPort, int timeOutMillis) {
        // Any Open port on other machine
        // openPort =  22 - ssh, 80 or 443 - webserver, 25 - mailserver etc.
        try (Socket soc = new Socket()) {
            soc.connect(new InetSocketAddress(addr, openPort), timeOutMillis);
            return true;
        } catch (IOException ex) {
            return false;
        }
    }

    public static int getLocalHost(Context context) {
        WifiManager wm = (WifiManager) context.getSystemService(Context.WIFI_SERVICE);
        return wm.getConnectionInfo().getIpAddress();
    }

    public static String formatToIPV4(int address) {
        return Formatter.formatIpAddress(address);
    }

    public static short getSubnetFormat() throws IOException, InterruptedException {
        Process proc = Runtime.getRuntime()
                .exec(new String[] {"su", "--command", "Djava.net.preferIPv4Stack=true"});
        proc.waitFor();

        InetAddress local = Inet4Address.getLocalHost();
        NetworkInterface networkInterface = NetworkInterface.getByInetAddress(local);
        return networkInterface.getInterfaceAddresses().get(1).getNetworkPrefixLength();
    }

    public static String getSubnetIP(int address)
    {
        String ipString = String.format(
                "%d.%d.%d",
                (address & 0xff),
                (address >> 8 & 0xff),
                (address >> 16 & 0xff));

        return ipString;
    }

    public static String getPiIP(Context context, String username, String password) {
        int localHost = SSHUtils.getLocalHost(context);
        String subnet = SSHUtils.getSubnetIP(localHost);
        List<String> hosts = SSHUtils.ping(subnet);

        for(String ip:hosts) {
            try {
                Session session = startSSH(username, ip, password);
                session.disconnect();
                return ip;
            } catch (JSchException e) {
                e.printStackTrace();
            }
        }
        return "Pi not found";
    }

    public static Session startSSH(String username, String host, String password) throws JSchException {
        JSch jsch = new JSch();
        Session session = jsch.getSession(username, host, 22);
        session.setPassword(password);

        Properties prop = new Properties();
        prop.put("StrictHostKeyChecking", "no");
        session.setConfig(prop);

        session.connect();

        System.out.println("SSH session to "+username+" established");

        return session;
    }

    public static int execSSHCmd(String cmd, Session session) {
        try{
            Channel channel = session.openChannel("exec");
            ((ChannelExec)channel).setCommand(cmd);
            channel.setInputStream(null);
            ((ChannelExec)channel).setErrStream(System.err);
            channel.setOutputStream(System.out);

            InputStream in=channel.getInputStream();
            StringBuilder output = new StringBuilder();
            int exitStatus;

            channel.connect();
            while (true) {
                for (int c; ((c = in.read()) >= 0);) {
                    output.append((char) c);
                }
                System.out.println(output);

                if (channel.isClosed()) {
                    if (in.available() > 0) continue;
                    exitStatus = channel.getExitStatus();
                    System.out.println("EXIT STATUS: "+exitStatus);
                    break;
                }
            }
            channel.disconnect();

            System.out.println("CMD:\n"+cmd+"\nSTATUS COMPLETE");
            return 200;
        } catch (JSchException | IOException e) {
            System.out.println(e.getMessage());
            return -1;
        }
    }

}
