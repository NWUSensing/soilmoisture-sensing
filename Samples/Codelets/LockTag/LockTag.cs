using System;
using System.Collections.Generic;
using System.Text;

// Reference the API
using ThingMagic;

namespace LockTag
{
    /// <summary>
    /// Sample program that sets an access password on a tag and
    /// locks its EPC.
    /// </summary>
    class Program
    {
        static void Usage()
        {
            Console.WriteLine(String.Join("\r\n", new string[] {
                    " Usage: "+"Please provide valid reader URL, such as: [-v] [reader-uri] [--ant n[,n...]]",
                    " -v : (Verbose)Turn on transport listener",
                    " reader-uri : e.g., 'tmr:///com4' or 'tmr:///dev/ttyS0/' or 'tmr://readerIP'",
                    " [--ant n[,n...]] : e.g., '--ant 1,2,..,n",
                    " Example: 'tmr:///com4' or 'tmr:///com4 --ant 1,2' or '-v tmr:///com4 --ant 1,2'"
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

                    TagReadData[] tagReads;
                    if (Reader.Region.UNSPEC == (Reader.Region)r.ParamGet("/reader/region/id"))
                    {
                        Reader.Region[] supportedRegions = (Reader.Region[])r.ParamGet("/reader/region/supportedRegions");
                        if (supportedRegions.Length < 1)
                        {
                            throw new FAULT_INVALID_REGION_Exception();
                        }
                        r.ParamSet("/reader/region/id", supportedRegions[0]);
                    }

                    // In the current system, sequences of Gen2 operations require Session 0,
                    // since each operation resingulates the tag.  In other sessions,
                    // the tag will still be "asleep" from the preceding singulation.
                    Gen2.Session oldSession = (Gen2.Session)r.ParamGet("/reader/gen2/session");
                    Gen2.Session newSession = Gen2.Session.S0;
                    Console.WriteLine("Changing to Session " + newSession + " (from Session " + oldSession + ")");
                    r.ParamSet("/reader/gen2/session", newSession);

                    // Create a simplereadplan which uses the antenna list created above
                    SimpleReadPlan plan = new SimpleReadPlan(antennaList, TagProtocol.GEN2,null,null,1000);
                    // Set the created readplan
                    r.ParamSet("/reader/read/plan", plan);

                    try
                    {
                        // Find a tag to work on
                        tagReads = r.Read(1000);
                        if (0 == tagReads.Length)
                        {
                            Console.WriteLine("No tags found to work on");
                            return;
                        }

                        TagData t = tagReads[0].Tag;

                        //Use first antenna for operation
                        if (antennaList != null)
                            r.ParamSet("/reader/tagop/antenna", antennaList[0]);

                        // Lock the tag
                        r.ExecuteTagOp(new Gen2.Lock(0, new Gen2.LockAction(Gen2.LockAction.EPC_LOCK)), t);
                        Console.WriteLine("Locked EPC of tag " + t);

                        // Unlock the tag
                        r.ExecuteTagOp(new Gen2.Lock(0, new Gen2.LockAction(Gen2.LockAction.EPC_UNLOCK)), t);
                        Console.WriteLine("Unlocked EPC of tag " + t);
                    }
                    finally
                    {
                        // Restore original settings
                        Console.WriteLine("Restoring Session " + oldSession);
                        r.ParamSet("/reader/gen2/session", oldSession);
                    }
                }
            }
            catch (ReaderException re)
            {
                Console.WriteLine("Error: " + re.Message);
            }
            catch (Exception ex)
            {
                Console.WriteLine("Error: " + ex.Message);
            }
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
