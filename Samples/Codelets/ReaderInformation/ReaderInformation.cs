using System;
using System.Collections.Generic;
using System.Text;

// Reference the API
using ThingMagic;

namespace ReaderInformation
{
    /// <summary>
    /// Sample program to get reader information from the connected reader
    /// </summary>
    class ReaderInformation
    {
        static void Usage()
        {
            Console.WriteLine(String.Join("\r\n", new string[] {
                    " Usage: "+"Please provide valid reader URL, such as: [-v] [reader-uri]",
                    " -v : (Verbose)Turn on transport listener",
                    " reader-uri : e.g., 'tmr:///com4' or 'tmr:///dev/ttyS0/' or 'tmr://readerIP'",
                    " Example: 'tmr:///com4'' or '-v tmr:///com4'"
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

            try
            {
                // Create Reader object, connecting to physical device.
                // Wrap reader in a "using" block to get automatic
                // reader shutdown (using IDisposable interface).
                using (Reader r = Reader.Create(args[0]))
                {
                    //Uncomment this line to add default transport listener.
                    //r.Transport += r.SimpleTransportListener;

                    try
                    {
                        /* MercuryAPI tries connecting to the module using default baud rate of 115200 bps.
                         * The connection may fail if the module is configured to a different baud rate. If
                         * that is the case, the MercuryAPI tries connecting to the module with other supported
                         * baud rates until the connection is successful using baud rate probing mechanism.
                         */
                        r.Connect();
                    }
                    catch (Exception ex)
                    {
                        if (ex.Message.Contains("The operation has timed out") && r is SerialReader)
                        {
                            int currentBaudRate = 0;
                            // Default baudrate connect failed. Try probing through the baudrate list
                            // to retrieve the module baudrate
                            ((SerialReader)r).probeBaudRate(ref currentBaudRate);
                            //Set the current baudrate so that next connect will use this baudrate.
                            r.ParamSet("/reader/baudRate", currentBaudRate);
                            // Now connect with current baudrate
                            r.Connect();
                        }
                        else
                        {
                            throw new Exception(ex.Message);
                        }
                    }
                    if (Reader.Region.UNSPEC == (Reader.Region)r.ParamGet("/reader/region/id"))
                    {
                        Reader.Region[] supportedRegions = (Reader.Region[])r.ParamGet("/reader/region/supportedRegions");
                        if (supportedRegions.Length < 1)
                        {
                            throw new FAULT_INVALID_REGION_Exception();
                        }
                        r.ParamSet("/reader/region/id", supportedRegions[0]);
                    }

                    // Create reader information obj
                    ReaderInformation readInfo = new ReaderInformation();
                    Console.WriteLine("Reader information of connected reader");

                    // Hardware info
                    readInfo.Get("Hardware", "/reader/version/hardware", r);

                    // Serial info
                    readInfo.Get("Serial", "/reader/version/serial", r);

                    // Model info
                    readInfo.Get("Model", "/reader/version/model", r);

                    // Software info
                    readInfo.Get("Software", "/reader/version/software", r);

                    // Reader uri info
                    readInfo.Get("Reader URI", "/reader/uri", r);

                    // Product id info
                    readInfo.Get("Product ID", "/reader/version/productID", r);

                    // Product group id info
                    readInfo.Get("Product Group ID", "/reader/version/productGroupID", r);

                    // Product group info
                    readInfo.Get("Product Group", "/reader/version/productGroup", r);

                    // Reader description info
                    readInfo.Get("Reader Description", "/reader/description", r);
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

        /// <summary>
        /// Get the data for the specified parameter from the connected reader
        /// </summary>
        /// <param name="paramString">Parameter descritpion</param>
        /// <param name="parameter">Parameter to get</param>
        /// <param name="rdrObj">Reader object</param>        
        public void Get(string paramString, string parameter, Reader rdrObj)
        {
            try
            {
                // Get data for the requested parameter from the connected reader
                Console.WriteLine();
                Console.WriteLine(paramString + ": " + rdrObj.ParamGet(parameter));
            }
            catch (Exception ex)
            {
                if ((ex is FeatureNotSupportedException) || (ex is ArgumentException))
                {
                    Console.WriteLine(paramString + ": " + parameter + " - Unsupported");
                }
                else
                {
                    Console.WriteLine(paramString + " : " + ex.Message);
                }
            }
        }
    }
}
