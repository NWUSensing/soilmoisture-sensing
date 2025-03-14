﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Windows.Data;
using System.Windows.Controls;
using System.Globalization;
using System.Windows;
using System.Security.AccessControl;
using System.IO;
using System.Security.Principal;

namespace ThingMagic.URA2
{
    /// <summary>
    /// Used to make visible and disable default text "select" on column selection combobox
    /// </summary>
    public class NullToVisibilityConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
        {
            return value == null ? Visibility.Visible : Visibility.Collapsed;
        }

        public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        {
            throw new NotImplementedException();
        }
    }

    public static class Utilities
    {

       #region NMV2D
      
      public const string WvonBraun = "C19";
        //sub type
      public const string NMV2D = "564";

       #endregion NMV2D


        #region IMPINJ

        //Impinj = 001
        public const string Impinj              = "001";
        public const string ImpinjXTID          = "801";
        //sub type
        public const string ImpinjOld           = "000";
        public const string ImpinjAnchor        = "040";
        public const string ImpinjMonza         = "050";
        public const string ImpinjMonzaID_2     = "060";
        public const string ImpinjMonaco        = "061";
        public const string ImpinjMonza2        = "070";
        public const string ImpinjMonza2A       = "071";
        public const string ImpinjMonzaID_3     = "080";
        public const string ImpinjMonzaID_3A    = "081";
        public const string ImpinjMonzaID_3B    = "082";
        public const string ImpinjMonzaID_3C    = "083";
        public const string ImpinjMonza3        = "090";
        public const string ImpinjMonza_3A      = "091";
        public const string ImpinjMonza_3B      = "092";
        public const string ImpinjMonza_3C      = "093";
        public const string ImpinjMonza_3D      = "0A0";

        public const string ImpinjMonza_4D      = "100";
        public const string ImpinjMonza_4E      = "10C";
        public const string ImpinjMonza_4I      = "106";
        public const string ImpinjMonza_4U      = "104";
        public const string ImpinjMonza_4QT     = "105";
        public const string ImpinjMonza_5       = "130";
        public const string ImpinjMonza_X2K     = "140";
        public const string ImpinjMonza_R6      = "160";
        public const string ImpinjMonza_R6_P    = "170";
        public const string ImpinjMonza_S6_C    = "171";

        #endregion IMPINJ

        #region TI
        //TI = 002
        public const string  TI = "002";

        #endregion TI

        #region ALIEN

        //Alien = 003
        public const string Alien           = "003";
        //sub type
        public const string AlienHiggs2     = "411";
        public const string AlienHiggs3     = "412";
        public const string AlienHiggs4     = "414";
        public const string AlienHiggsEC    = "811";

        #endregion ALIEN


        //Phillips = 004
        public const string Phillips = "004";
        //sub type
        public const string PhillipsUCODESL3 = "001";

        #region ATMEL

        public const string ATMEL   = "005";

        #endregion ATMEL

        #region NXP

        //NXP=006 and 806
        public const string NXP                 = "006";
        public const string NXPv2               = "C06";
        public const string NXPXTID             = "806";
         //sub type
        public const string NXP_G2              = "001";
        public const string NXP_G2_XM           = "003";
        public const string NXP_G2_XL           = "004";
        public const string NXP_G2_iL_V0        = "806";
        public const string NXP_G2_iL_V2        = "906";
        public const string NXP_G2_iL_V6        = "B06";
        public const string NXP_G2_iL_Plus_V0   = "807";
        public const string NXP_G2_iL_Plus_V2   = "907";
        public const string NXP_G2_iL_Plus_V6   = "B07";
        public const string NXP_G2_IM           = "80A";
        public const string NXP_G2_IM_Plus      = "80B";
        public const string NXPI2C              = "98C";
        public const string NXP_UCODE_8         = "894";
        public const string NXP_UCODE_8m        = "994";

        public const string NXP_UCODE_7         = "810";
        public const string NXP_UCODE_7m        = "811";
        public const string NXP_UCODE_7xm       = "D12";
        public const string NXP_UCODE_7xm_Plus  = "D92";
        public const string NXP_UCODE_DNA       = "F92";

        public const string NXPI2C4011          = "80D";
        public const string NXPI2C4021          = "88D";

        #endregion NXP

        #region STMICRO

        // STMICRO=007
        public const string STMicro         = "007";

        // sub-type
        public const string STMicro_XRAG2   = "240";
        #endregion STMICRO

        #region EPMICRO

        public const string EPMicro = "008";

        #endregion EPMICRO

        #region MOTOROLA

        public const string MOTOROLA = "009";

        #endregion MOTOROLA

        #region SENTECH

        public const string SENTECH = "00A";

        #endregion SENTECH

        #region EMMICRO

        //Power-ID=00B
        //public const string PowerID = "00B";
        public const string EMMICRO                 = "00B";
        public const string EMMICROXTID             = "80B";

        public const string EMMICRO_EM4126_V0       = "0C0";
        public const string EMMICRO_EM4126_V1       = "0C1";
        public const string EMMICRO_EM4126_V2       = "0C2";
        public const string EMMICRO_EM4126_V3       = "0C3";
        public const string EMMICRO_EM4126_V4       = "0C4";
        public const string EMMICRO_EM4126_V5       = "0C5";
        public const string EMMICRO_EM4126_V6       = "0C6";
        public const string EMMICRO_EM4126_V7       = "0C7";

        public const string EMMICRO_EM4124          = "080";
        public const string EMMICRO_EM4124_D        = "082";

        public const string EMMICRO_EM4324_V1       = "001";
        public const string EMMICRO_EM4324_V2       = "002";

        public const string EMMICRO_EM4325_V11      = "040";
        public const string EMMICRO_EM4325_V21      = "044";
        public const string EMMICRO_EM4325_V31      = "048";
        public const string EMMICRO_EM4325_V41      = "04C";

        public const string EMMICRO_EM4423_S        = "0A0";
        public const string EMMICRO_EM4423_L        = "0A1";
        public const string EMMICRO_EM4423_S_PLUS   = "0A2";
        public const string EMMICRO_EM4423_L_PLUS   = "0A3";
        public const string EMMICRO_EM4423T_S       = "0A4";
        public const string EMMICRO_EM4423T_L       = "0A5";
        public const string EMMICRO_EM4423T_S_PLUS  = "0A6";
        public const string EMMICRO_EM4423T_L_PLUS  = "0A7";

        #endregion EMMICRO

        #region RENESAS

        public const string RENESAS = "00C";

        #endregion RENESAS

        #region MSTAR

        public const string MSTAR = "00D";

        #endregion MSTAR

        #region TYCO

        public const string TYCO = "00E";

        #endregion TYCO

        #region QUANRAY

        //Quanray=00F
        public const string Quanray = "00F";
        //Sub Type
        public const string QuanrayQstar5 = "301";

        #endregion QUANRAY

        #region FUJITSU

        //Quanray=00F
        public const string FUJITSU = "010";
        //Sub Type
        public const string FUJUTSU_64K = "021";

        #endregion FUJITSU

        //RF Micron= 824
        public const string RFMicron = "824";
        //Sub Type
        public const string RFMicronMagnus = "02E";

        
        
        //sub type
        public const string PowerIDEmMicroWithOutTamper = "001";
        public const string PowerIDEmMicroWithTamper = "002";

        //Hitchi = 00C
        public const string Hitchi = "00C";

        //IDS = 361
        public const string IDS = "361";
        //sub type
        public const string IDSSL900A = "139";

        #region RAMTRON

        // RAMTRON = 016
        public const string RAMTRON = "016";
        //sub type
        public const string RAMTRON_WM72016 = "216";

        #endregion RAMTRON


        #region TEGO

        // TEGO = 017
        public const string Tego = "017";
        //sub type
        public const string Tego4K  = "000";
        public const string Tego8K = "008";
        public const string Tego24K = "01C";

        // TEGO = 817
        public const string TegoXTID    = "817";
        //sub type
        public const string TTegoXTID8K = "000";

        #endregion TEGO

        #region FUDAN

        //Fudan = 827
        public const string Fudan = "827";
        //sub type
        public const string FudanDT160 = "001";

        #endregion FUDAN

        /// <summary>
        /// Converts Hexadecimal EPC into reversed B36 encoded string
        /// </summary>
        /// <param name="hex"></param>
        /// <returns></returns>
        public static String ConvertHexToBase36(String hex)
        {
            if (hex.Length > 0)
            {
                BigInteger big = new BigInteger(hex.ToUpper(), 16);
                StringBuilder sb = new StringBuilder(big.ToString(36));
                char[] charArray = sb.ToString().ToCharArray();
                Array.Reverse(charArray);
                return new string(charArray).ToUpper();
            }
            else
            {
                return string.Empty;
            }
        }

        /// <summary>
        /// Converts B36 encoded string into Hexadecimal EPC
        /// </summary>
        /// <param name="b36"></param>
        /// <returns>Hex string</returns>
        public static String ConvertBase36ToHex(String b36)
        {
            if (b36.Length > 0)
            {
                StringBuilder sb = new StringBuilder(b36.ToUpper());
                char[] charArray = sb.ToString().ToCharArray();
                Array.Reverse(charArray);
                BigInteger big = new BigInteger(new string(charArray), 36);
                if (b36.Length != big.ToHexString().Length)
                {
                    return big.ToHexString().TrimStart('0');
                }
                else
                {
                    return big.ToHexString();
                }
            }
            else
            {
                return string.Empty;
            }
        }

        /// <summary>
        /// Convert ascii value to hex value
        /// </summary>
        /// <param name="hex"></param>
        /// <returns>Hex value</returns>
        public static string AsciiStringToHexString(string asciiString)
        {
            string hex = "";
            if (asciiString.Length > 0)
            {
                foreach (char c in asciiString)
                {
                    int tmp = c;
                    hex += String.Format("{0:x2}", (uint)System.Convert.ToUInt32(tmp.ToString()));
                }
                return hex.ToUpper();
            }
            else
            {
                return hex;
            }
        }

        /// <summary>
        /// Convert hex value to ascii value
        /// </summary>
        /// <param name="hexString"></param>
        /// <returns>Ascii value</returns>
        public static string HexStringToAsciiString(string hexString)
        {
            string StrValue = "";
            if (hexString.Length > 0)
            {
                while (hexString.Length > 0)
                {
                    StrValue += System.Convert.ToChar(System.Convert.ToUInt32(hexString.Substring(0, 2), 16)).ToString();
                    hexString = hexString.Substring(2, hexString.Length - 2);
                }
                return StrValue;
            }
            else
            {
                return StrValue;
            }
        }

        /// <summary>
        /// Creates a byte array from the hexadecimal string. Each two characters are combined
        /// to create one byte. First two hexadecimal characters become first byte in returned array.
        /// Non-hexadecimal characters are ignored. 
        /// </summary>
        /// <param name="hexString">string to convert to byte array</param>
        /// <param name="discarded">number of characters in string ignored</param>
        /// <returns>byte array, in the same left-to-right order as the hexString</returns>
        public static byte[] GetBytes(string hexString, out int discarded)
        {
            discarded = 0;
            string newString = "";
            char c;
            // remove all none A-F, 0-9, characters
            for (int i = 0; i < hexString.Length; i++)
            {
                c = hexString[i];
                if (IsHexDigit(c))
                    newString += c;
                else
                    discarded++;
            }
            // if odd number of characters, discard last character
            if (newString.Length % 2 != 0)
            {
                discarded++;
                newString = newString.Substring(0, newString.Length - 1);
            }

            int byteLength = newString.Length / 2;
            byte[] bytes = new byte[byteLength];
            string hex;
            int j = 0;
            for (int i = 0; i < bytes.Length; i++)
            {
                hex = new String(new Char[] { newString[j], newString[j + 1] });
                bytes[i] = HexToByte(hex);
                j = j + 2;
            }
            return bytes;
        }

        /// <summary>
        /// Returns true is c is a hexadecimal digit (A-F, a-f, 0-9)
        /// </summary>
        /// <param name="c">Character to test</param>
        /// <returns>true if hex digit, false if not</returns>
        public static bool IsHexDigit(Char c)
        {
            int numChar;
            int numA = Convert.ToInt32('A');
            int num1 = Convert.ToInt32('0');
            c = Char.ToUpper(c);
            numChar = Convert.ToInt32(c);
            if (numChar >= numA && numChar < (numA + 6))
                return true;
            if (numChar >= num1 && numChar < (num1 + 10))
                return true;
            return false;
        }

        /// <summary>
        /// Converts 1 or 2 character string into equivalant byte value
        /// </summary>
        /// <param name="hex">1 or 2 character string</param>
        /// <returns>byte</returns>
        public static byte HexToByte(string hex)
        {
            if (hex.Length > 2 || hex.Length <= 0)
                throw new ArgumentException("hex must be 1 or 2 characters in length");
            byte newByte = byte.Parse(hex, System.Globalization.NumberStyles.HexNumber);
            return newByte;
        }

        /// <summary>
        /// Check whether the string is in hex or decimal
        /// ex: 0xFF or 12
        /// </summary>
        /// <param name="hex">string in hex or decimal</param>
        /// <returns>Returns the converted integer value if convertion is success else throws exception</returns>
        public static UInt32 CheckHexOrDecimal(string hex)
        {
            int prelen = 0;
            UInt32 decValue = 0;
            if (hex.EndsWith("0x") || hex.EndsWith("0X"))
            {
                throw new Exception("Not a valid hex number");
            }
            // If string is prefixed with 0x
            if (hex.StartsWith("0x") || hex.StartsWith("0X"))
            {
                prelen = 2;
                // Strikeout the 0x and extract the remaining string
                string hexstring = hex.Substring(prelen);           
                // Check whether the string is valid hex number
                if (UInt32.TryParse(hexstring, NumberStyles.HexNumber, CultureInfo.CurrentCulture, out decValue))
                {
                    decValue = UInt32.Parse(hexstring, System.Globalization.NumberStyles.HexNumber);
                    return decValue;
                }
                else
                {
                    throw new Exception("Not a valid hex number");
                }
            }
            else
            {
                // If the string is not prefixed with 0x
                // Check whether the string is valid decimal number
                if (AreAllValidNumericChars(hex))
                {
                    return Convert.ToUInt32(hex);
                }
                else
                {
                    throw new Exception("Not a valid number");
                }
            }
        }

        /// <summary>
        /// Check whether the string has valid numbers or no
        /// </summary>
        /// <param name="str">string</param>
        /// <returns>True: if string is valid number else False</returns>
        public static bool AreAllValidNumericChars(string str)
        {
            foreach (char c in str)
            {
                if (!Char.IsNumber(c)) return false;
            }
            return true;
        }

        /// <summary>
        /// Check whether the string has only double values or no
        /// </summary>
        /// <param name="str">string, accepts only - and . special characters</param>
        /// <returns>True: if string is double else False</returns>
        public static bool DoubleCharChecker(string str)
        {
            foreach (char c in str)
            {
                if (c.Equals('-'))
                    return true;

                else if (c.Equals('.'))
                    return true;

                else if (Char.IsNumber(c))
                    return true;
            }
            return false;
        }

        /// <summary>
        /// Check whether the hex string is prefix with 0x
        /// </summary>
        /// <param name="str">string, accepts only x </param>
        /// <returns>True: if string is double else False</returns>
        public static bool HexStringChecker(string str)
        {
            int hexNumber;
            foreach (char c in str)
            {
                if (c.Equals('x'))
                    return true;

                else if (int.TryParse(c.ToString(), NumberStyles.HexNumber, CultureInfo.CurrentCulture, out hexNumber))
                    return true;
            }
            return false;
        }

        /// <summary>
        /// Remove prefix 0x in a hexstring
        /// </summary>
        /// <param name="hexstring">hex string</param>
        /// <returns>hex string with 0x removed</returns>
        public static string RemoveHexstringPrefix(string hexstring)
        {
            int prelen = 0;
            if (hexstring.EndsWith("0x") || hexstring.EndsWith("0X"))
            {
                throw new Exception("Not a valid hex number");
            }
            if (hexstring.StartsWith("0x") || hexstring.StartsWith("0X"))
            {
                prelen = 2;
                hexstring = hexstring.Substring(prelen);
            }
            return hexstring;
        }

        /// <summary>
        /// Adds an ACL entry on the specified file for the specified account to 
        /// give every user of the local machine rights to modify configuration file
        /// </summary>
        /// <param name="fileName"></param>
        public static void SetEditablePermissionOnConfigFile(string fileName)
        {
            // Get a FileSecurity object that represents the 
            // current security settings.
            FileSecurity accessControl = File.GetAccessControl(fileName);

            // Give every user of the local machine rights to modify configuration file
            var userGroup = new NTAccount("BUILTIN\\Users");
            var userIdentityReference = userGroup.Translate(typeof(SecurityIdentifier));

            // Add the FileSystemAccessRule to the security settings.
            accessControl.SetAccessRule(
                new FileSystemAccessRule(userIdentityReference,
                                         FileSystemRights.FullControl,
                                         AccessControlType.Allow));
            // Set the new access settings.
            File.SetAccessControl(fileName, accessControl);
        }
    }

    /// <summary>
    /// Convertor to convert read power values between slider and textbox
    /// </summary>
    public class ReadPowerConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, System.Globalization.CultureInfo culture)
        {
            if (value != null)
            {
                double dblValue = (double)value;
                return Math.Round(dblValue,1);
            }
            return 0;
        }

        public object ConvertBack(object value, Type targetType, object parameter, System.Globalization.CultureInfo culture)
        {
            if (value != null)
            {
                try
                {
                    if (value.ToString() != "")
                    {
                        double ret = double.Parse(value.ToString());
                        return Math.Round(ret, 1);
                    }
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message, "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
            return 0;
        }
    }
}