using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
// for Thread.Sleep
using System.Threading;
using System.Linq;


// Reference the API
using ThingMagic;

namespace ReadAsync
{
    /// <summary>
    /// Sample program that reads tags in the background and prints the
    /// tags found.
    /// </summary>
    class Program
    {
        static int epoch = 0;
        static void Usage()
        {
            Console.WriteLine(String.Join("\r\n", new string[] {
                    "Usage: "+"Please provide valid arguments, such as:",
                    "tmr:///com4 or tmr:///com4 --ant 1,2",
                    "tmr://my-reader.example.com or tmr://my-reader.example.com --ant 1,2"
            }));
            Environment.Exit(1);
        }
        static void Main(string[] args)
        {
            // Program setup
            if (1 > args.Length)
            {
                Usage();
            }
            int[] antennaList = null;
            for (int nextarg = 1; nextarg < args.Length; nextarg++)
            {
                string arg = args[nextarg];
                if (arg.Equals("--ant"))
                {
                    if (null != antennaList)
                    {
                        Console.WriteLine("Duplicate argument: --ant specified more than once");
                        Usage();
                    }
                    antennaList = ParseAntennaList(args, nextarg);
                    nextarg++;
                }
                else
                {
                    Console.WriteLine("Argument {0}:\"{1}\" is not recognized", nextarg, arg);
                    Usage();
                }
            }

            try
            {
                // Create Reader object, connecting to physical device.
                // Wrap reader in a "using" block to get automatic
                // reader shutdown (using IDisposable interface).
                using (Reader r = Reader.Create(args[0]))
                {
                    //Uncomment this line to add default transport listener.
                    //r.Transport += r.SimpleTransportListener;

                    r.Connect();
                    if (Reader.Region.UNSPEC == (Reader.Region)r.ParamGet("/reader/region/id"))
                    {
                        Reader.Region[] supportedRegions = (Reader.Region[])r.ParamGet("/reader/region/supportedRegions");
                        if (supportedRegions.Length < 1)
                        {
                            throw new FAULT_INVALID_REGION_Exception();
                        }
                        r.ParamSet("/reader/region/id", supportedRegions[0]);
                    }
                    string model = r.ParamGet("/reader/version/model").ToString();
                    if ((model.Equals("M6e Micro") || model.Equals("M6e Nano") || model.Equals("Sargas")) && antennaList == null)
                    {
                        Console.WriteLine("Module doesn't has antenna detection support please provide antenna list");
                        Usage();
                    }
                    // Create a simplereadplan which uses the antenna list created above
                    SimpleReadPlan plan = new SimpleReadPlan(antennaList, TagProtocol.GEN2,null,null,1000);
                    // Set the created readplan
                    r.ParamSet("/reader/read/plan", plan);
                    r.ParamSet("/reader/radio/readPower", 3000);  // 设置读取功率

                    //string antennas = r.ParamGet("/reader/antenna/portList").ToString();
                    // 设置频率
                    List<UInt32[]> freqs_list = new List<UInt32[]>();
                    for (int idx = 0; idx != 16; ++idx)
                    {
                        UInt32[] hoptable = new UInt32[] { 920625 + (UInt32)idx * 250, 920625 + (UInt32)idx * 250 };
                        freqs_list.Add(hoptable);
                        // freqs_list.Add(hoptable);  // 那个ReadAsync设置有点问题，只能跑1s（感觉）
                    }
                    // var hptime = r.ParamGet("/reader/region/hopTime");
                    // Console.WriteLine("hoptime type: {0}", hptime);
                    //uint time = 500;
                    //r.ParamSet("/reader/region/hopTime", time);
                    // r.ParamSet("/reader/read/asyncOnTime", 1000);  // Default:250ms同步读取时间
                    // r.ParamSet("/reader/read/asyncOffTime", 1000);
                    //r.ParamSet("/reader/region/id", Reader.Region.PRC);
                    /*
                    var freqs = r.ParamGet("/reader/region/hoptable");
                    var freqs_time = r.ParamGet("/reader/region/hopTime");
                    var TxPower = r.ParamGet("/reader/radio/readPower");
                    var a = r.ParamGet("/reader/antenna/portList");
                    var region = r.ParamGet("/reader/region/id");
                   

                    //Console.WriteLine("freqs: {0}\n freq_time: {1}\n AntennaList: {2}", freqs, freqs_time, antennas);
                    */

                    string filepath = "./ThingMagicReader_test.csv";
                    // FileStream file = new FileStream(filepath, FileMode.Append);
                    // StreamWriter writer = new StreamWriter(file);

                    // Create and add tag listener
                    r.TagRead += delegate(Object sender, TagReadDataEventArgs e)
                    {
                        // Console.WriteLine("Background read: " + e.TagReadData);
                        using (FileStream file = new FileStream(filepath, FileMode.Append))
                        {
                            using (StreamWriter writer = new StreamWriter(file))
                            {

                                
                        writer.WriteLine("{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}", e.TagReadData.EpcString.Replace(" ", ""),
                            e.TagReadData.Frequency,
                            e.TagReadData.Phase,
                            e.TagReadData.Rssi,
                            0, 0,
                            e.TagReadData.Antenna,
                            e.TagReadData.Time,
                            epoch);
             
                        Console.WriteLine("{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}\n", e.TagReadData.EpcString.Replace(" ", ""),
                            e.TagReadData.Frequency,
                            e.TagReadData.Phase,
                            e.TagReadData.Rssi,
                            0, 0,
                            e.TagReadData.Antenna,
                            e.TagReadData.Time,
                            epoch);

                            }
                        }
                    };

                    r.ParamSet("/reader/gen2/tagEncoding", Gen2.TagEncoding.M4);
                    r.ParamSet("/reader/gen2/q",  new Gen2.DynamicQ());
                    r.ParamSet("/reader/gen2/BLF", Gen2.LinkFrequency.LINK250KHZ);
                    r.ParamSet("/reader/gen2/tari", Gen2.Tari.TARI_6_25US);
                    r.ParamSet("/reader/gen2/session", Gen2.Session.S0);
                    r.ParamSet("/reader/gen2/target",Gen2.Target.AB);
                    r.ParamSet("/reader/region/id",Reader.Region.PRC);
               

                    // Create and add read exception listener
                    r.ReadException += new EventHandler<ReaderExceptionEventArgs>(r_ReadException);            

                    // Search for tags in the background
                    while (true)
                    {
                        foreach (var hoptable in freqs_list)
                        {
                            int times = 6;
                            r.ParamSet("/reader/region/hopTable", hoptable);
                            while (times > 0)
                            {
                                r.StartReading();
                            
                                Console.WriteLine("\r\n<Do other work here>\r\n");
                                Thread.Sleep(400);
                                //Console.WriteLine("\r\n<Do other work here>\r\n");
                                //Thread.Sleep(500);
                                r.StopReading(); 
                                //Thread.Sleep(200);
                                times = times - 1;
                                //break;
                            }
                        }
                        epoch = epoch + 1;
                        //break;
                    }
                    //writer.Close();
                    //file.Close();
                }
            }
            catch (ReaderException re)
            {
                Console.WriteLine("Error, catch1: " + re.Message);
                Console.Out.Flush();
            }
            catch (Exception ex)
            {
                Console.WriteLine("Error, catch2: " + ex.Message);
            }
        }

        private static void r_ReadException(object sender, ReaderExceptionEventArgs e)
        {
            Console.WriteLine("Error: " + e.ReaderException.Message);
        }

        #region ParseAntennaList

        private static int[] ParseAntennaList(IList<string> args, int argPosition)
        {
            int[] antennaList = null;
            try
            {
                string str = args[argPosition + 1];
                antennaList = Array.ConvertAll<string, int>(str.Split(','), int.Parse);
                if (antennaList.Length == 0)
                {
                    antennaList = null;
                }
            }
            catch (ArgumentOutOfRangeException)
            {
                Console.WriteLine("Missing argument after args[{0:d}] \"{1}\"", argPosition, args[argPosition]);
                Usage();
            }
            catch (Exception ex)
            {
                Console.WriteLine("{0}\"{1}\"", ex.Message, args[argPosition + 1]);
                Usage();
            }
            return antennaList;
        }

        #endregion
    }
}
