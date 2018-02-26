package com.example.itamar.legaltech;

import android.Manifest;
import android.content.pm.PackageManager;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaRecorder;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;

import java.io.DataOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.Socket;
import java.net.UnknownHostException;

public class MainActivity extends AppCompatActivity {

    // Button startButton, stopButton;

    public byte[] buffer;
    private int port = 5006;

    AudioRecord recorder;
    static Socket socket;
    private int sampleRate = 16000; // 44100 for music
    private int channelConfig = AudioFormat.CHANNEL_CONFIGURATION_MONO;
    private int audioFormat = AudioFormat.ENCODING_PCM_8BIT;
    int minBufSize = AudioRecord.getMinBufferSize(sampleRate, channelConfig, audioFormat);
    private boolean status = false;
    static String IP = "192.168.43.18";
    ImageView ivMic;
    int res;
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);



//        // Set the color
//        root.setBackgroundColor(getResources().getColor(android.R.color.red));

        if (ContextCompat.checkSelfPermission(this,
                Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {

            ActivityCompat.requestPermissions(this  ,
                    new String[]{Manifest.permission.RECORD_AUDIO},
                    res);

        }

//        startButton = (Button) findViewById(R.id.start_button);
//        stopButton = (Button) findViewById(R.id.stop_button);
//
//        startButton.setOnClickListener(startListener);
//        stopButton.setOnClickListener(stopListener);

        ivMic = (ImageView) findViewById(R.id.ivMic);
        ivMic.setOnClickListener(micClickListener);
    }

    private final View.OnClickListener micClickListener = new View.OnClickListener(){
        @Override
        public void onClick(View arg0) {
            if(status){
                status = false;
                ivMic.setImageResource(R.mipmap.micon);
                try {
                    socket.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
                recorder.release();
                Log.d("VS", "Recorder released");
            }else{
                status = true;
                ivMic.setImageResource(R.mipmap.micoff);
                startStreaming();
            }
        }
    };

//    private final View.OnClickListener stopListener = new View.OnClickListener() {
//
//        @Override
//        public void onClick(View arg0) {
//            status = false;
//            ivMic.setImageDrawable(getDrawable(R.drawable.micoff));
//            try {
//                socket.close();
//            } catch (IOException e) {
//                e.printStackTrace();
//            }
//            recorder.release();
//            Log.d("VS", "Recorder released");
//        }
//
//    };

//    private final View.OnClickListener startListener = new View.OnClickListener() {
//
//        @Override
//        public void onClick(View arg0) {
//            status = true;
//            ivMic.setImageDrawable(getDrawable(R.drawable.micon));
//            startStreaming();
//        }
//
//    };
    private static int[] mSampleRates = new int[] { 8000, 11025, 22050, 44100 };
    public AudioRecord findAudioRecord() {
        for (int rate : mSampleRates) {
            for (short audioFormat : new short[]{AudioFormat.ENCODING_PCM_8BIT, AudioFormat.ENCODING_PCM_16BIT}) {
                for (short channelConfig : new short[]{AudioFormat.CHANNEL_IN_MONO, AudioFormat.CHANNEL_IN_STEREO}) {
                    try {
                        Log.d("TAG", "Attempting rate " + rate + "Hz, bits: " + audioFormat + ", channel: "
                                + channelConfig);
                        int bufferSize = AudioRecord.getMinBufferSize(rate, channelConfig, audioFormat);

                        if (bufferSize != AudioRecord.ERROR_BAD_VALUE) {
                            // check if we can instantiate and have a success44100, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT
                            AudioRecord recorder = new AudioRecord(MediaRecorder.AudioSource.DEFAULT, 44100, AudioFormat.CHANNEL_IN_MONO, audioFormat, AudioFormat.ENCODING_PCM_16BIT);

                            if (recorder.getState() == AudioRecord.STATE_INITIALIZED)
                                return recorder;
                        }
                    } catch (Exception e) {
                        Log.e("TAG", rate + "Exception, keep trying.", e);
                    }
                }
            }
        }
        return null;
    }

    public void startStreaming() {


        Thread streamThread = new Thread(new Runnable() {

            @Override
            public void run() {
                try {


                    try {
                        socket = new Socket(IP, 5006);
                    } catch (IOException e) {
                        e.printStackTrace();
                    }



                   // DatagramSocket socket = new DatagramSocket();
                    Log.d("VS", "Socket Created");

                    int minBufSize = AudioRecord.getMinBufferSize(sampleRate, channelConfig, audioFormat);

                    byte[] buffer = new byte[minBufSize];

                    Log.d("VS", "Buffer created of size " + minBufSize);
                    DatagramPacket packet;

                    final InetAddress destination = InetAddress.getByName(IP);
                    Log.d("VS", "Address retrieved");


                    //recorder = findAudioRecord();

                    final int recordingBufferSize = AudioRecord.getMinBufferSize(16000,
                            AudioFormat.CHANNEL_IN_MONO,
                            AudioFormat.ENCODING_PCM_16BIT);
                    final int size = recordingBufferSize*4;
                    recorder = new AudioRecord(MediaRecorder.AudioSource.DEFAULT,
                            16000,
                            AudioFormat.CHANNEL_IN_MONO,
                            AudioFormat.ENCODING_PCM_16BIT,
                            size);

                    recorder.startRecording();


                    while (status == true) {


                        //reading data from MIC into buffer
                        minBufSize = recorder.read(buffer, 0, buffer.length);
                        packet = new DatagramPacket(buffer, buffer.length, destination, port);

                        OutputStream out = socket.getOutputStream();
                        DataOutputStream dos = new DataOutputStream(out);

                        //dos.writeInt(buffer.length);

                        dos.write(buffer, 0, buffer.length);

//                        //putting buffer in the packet
//                        packet = new DatagramPacket(buffer, buffer.length, destination, port);
//
//                        socket.send(packet);
//                        System.out.println("MinBufferSize: " + minBufSize);
//

                    }


                } catch (UnknownHostException e) {
                    Log.e("VS", "UnknownHostException");
                } catch (IOException e) {
                    e.printStackTrace();
                    Log.e("VS", "IOException");
                }
            }

        });
        streamThread.start();
    }
}