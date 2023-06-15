#**********************************************************************
#     Generate One Call Buffer Process
#**********************************************************************
# This script will automate the process for generating Utility Buffer
# Boundaries for the use of Missouri One Call.
#**********************************************************************
# Created By: Mark Rees, GIS Analyst, City of Columbia Missouri
#**********************************************************************
# Last Modified By: Mark Rees
#**********************************************************************
# Last Modified On: November 24, 2021
#**********************************************************************

#Import Required Modules
import arcpy
from arcpy import env
arcpy.env.overwriteOutput = True
import os
from zipfile import ZipFile
import shutil
from datetime import datetime

#Function to write to Log File

def WriteToLog(string):
     
    #Retrieve the current system date time stamp

    now = datetime.now()

    CurrentDay = now.strftime("%d")
    CurrentMonth = now.strftime("%m")
    CurrentYear = now.strftime("%Y")
    time = now.strftime("%H:%M:%S")

    SystemDateTime = CurrentMonth + "_" + CurrentDay + "_" + CurrentYear 
    FileName = "MissouriOneCall_"+SystemDateTime+".txt"
    FileName = FileName.replace(":","_")
    
    LogFilePath = "S:/WL/ScriptLogging/"+FileName
    if(os.path.exists(LogFilePath) == False):
     LogFile = open('S:/WL/ScriptLogging/'+FileName,'a')
    else:
         LogFile = open('S:/WL/ScriptLogging/'+FileName,'a')

    LogFile.write(string + "--" + SystemDateTime + " -- " + time + "\n")


    #Generate FLAG for Creation of Additional Two Buffers (Electric/Fiber and Water/Sewer)

CreateEF_WS_Buffers = False


#Create Initial List Object To Store Extracted Feature Layers

ExtractionList = []
BufferResultList = []

ProblemFound = False







print("***************************************")
print("       Extracting Source Data.....")
print("***************************************\n")

print ("Creating Working File Geodatabase...\n")

#Copy the Original Zip File and Extract It

KBOX_DisasterFiles = "S:\\WL\\Disaster_Recovery\Disaster_Files.zip"
ExtractDestinationFolder = "C:\\Disaster_Recovery"

import zipfile
with zipfile.ZipFile(KBOX_DisasterFiles,"r") as zip_ref:
    zip_ref.extractall(ExtractDestinationFolder)

WriteToLog("Extracting Disaster Recovery Files...")
print("Disaster Files Extracted Successfully!")

 #Generate References to the Source Disaster Recovery File Geodatabases

DisasterCityFileGDB = "C:\Disaster_Recovery\Disaster_CityData.gdb"
DisasterFiberGDB = "C:\Disaster_Recovery\Disaster_Fiber.gdb"
DisasterElectricGDB = "C:\Disaster_Recovery\Disaster_Electric.gdb"

#Make Directory to Hold the Working File Geodatabase

path = "C:\\OneCallBufferCreation\\"
if os.path.exists(path) == True:
     shutil.rmtree(path)
     os.mkdir(path)
else:
      os.mkdir(path)



#Creating Working File Geodatabase
print("Generating Working File Geodatabase...")
WorkingFileGDB = "C:\OneCallBufferCreation\OneCallBuffers.gdb"
arcpy.CreateFileGDB_management("C:\OneCallBufferCreation", "OneCallBuffers.gdb")
WriteToLog("Working File GDB Created Successfully ")
print ("Working File GDB Created Successfully!\n")

print("Copying City, Fiber, and Electric Data into Working File Geodatbase...")

#Make a copy of the Required Disaster Recovery Data

print("Extracting Fiber Data From Disaster Recovery....\n")
OriginalFiberFC = DisasterCityFileGDB+"\WL_Fiber\Fiber"
WorkingFiberFC = WorkingFileGDB + "\Fiber"


#Create City Fiber Feature Layer

arcpy.MakeFeatureLayer_management(OriginalFiberFC, "CityFiber_lyr")
arcpy.SelectLayerByAttribute_management("CityFiber_lyr", "NEW_SELECTION", 
                                         "UG_OR_OH IN ('UG') OR UG_OR_OH IS NULL")
ExtractedFiberCount = arcpy.GetCount_management ("CityFiber_lyr")[0]

print ("Extracted " + str(ExtractedFiberCount)+ " City Fiber Features Successfully!")
WriteToLog("Extracted " + str(ExtractedFiberCount)+ " City Fiber Features Successfully!")

 #Add to Extraction List

ExtractionList.append(WorkingFiberFC)


arcpy.CopyFeatures_management("CityFiber_lyr", WorkingFiberFC)
CopiedFiberCount = arcpy.GetCount_management ("CityFiber_lyr")[0]

if(ExtractedFiberCount == CopiedFiberCount):
     print("Successfully Copied ALL Fiber Features into Working File Geodatabse!")
     WriteToLog("Successfully Copied ALL Fiber Features into Working File Geodatabse!")
else:
     print("There was a problem generating the Fiber Features From the Disaster Recovery Source Data")
     WriteToLog("There was a problem generating the Fiber Features From the Disaster Recovery Source Data")
     ProblemFound = True


#Determine if there were any issues, if so notify, if not continue...

if(ProblemFound == False):
 print("Extracting Fiber Optic Cable Data From Disaster Recovery....\n")
 
 #Create Fiber Optic Cable Feature Layer
 
 OriginalFiberOpticFC = DisasterFiberGDB+"\FiberOpticCable"
 WorkingFiberOpticCableFC = WorkingFileGDB + "\FiberOpticCable"

 arcpy.MakeFeatureLayer_management(OriginalFiberOpticFC, "FiberOptic_lyr")

 arcpy.SelectLayerByAttribute_management("FiberOptic_lyr", "NEW_SELECTION", 
                                          "(OverheadUnderground <> 'Overhead' OR OverheadUnderground IS NULL) AND (CableOwner = 'City' OR CableOwner IS NULL)")

ExtractedFiberOpticCount = arcpy.GetCount_management ("FiberOptic_lyr")[0]


arcpy.CopyFeatures_management("FiberOptic_lyr", WorkingFiberOpticCableFC)

CopiedFiberOpticCount = arcpy.GetCount_management (WorkingFiberOpticCableFC)[0]

if(ExtractedFiberOpticCount == CopiedFiberOpticCount):
     print("Successfully Copied ALL Fiber Optic Features into Working File Geodatabase!")
     WriteToLog("Successfully Copied ALL Fiber Optic Features into Working File Geodatabase!")

else:
     print("There was a problem generating the Fiber Optic Features From the Disaster Recovery Source Data")
     WriteToLog("There was a problem generating the Fiber Optic Features From the Disaster Recovery Source Data")
     ProblemFound = True

print ("Extracted " + str(ExtractedFiberOpticCount)+ " City Fiber Optic Cable Features Successfully!")
WriteToLog("Extracted " + str(ExtractedFiberOpticCount)+ " City Fiber Optic Cable Features Successfully!")

#Add to Extraction List

ExtractionList.append(WorkingFiberOpticCableFC)


#Create PW Fiber Optic Cable Feature Layer

if(ProblemFound == False):

 OriginalPWFiberOpticFC = DisasterFiberGDB+"\PW_streets\PW_Fiber_Optic_Cable"
 WorkingPWFiberOpticCableFC = WorkingFileGDB + "\PW_FiberOpticCable"

 arcpy.MakeFeatureLayer_management(OriginalPWFiberOpticFC, "PWFiberOptic_lyr")

 ExtractedPWFiberOpticCount = arcpy.GetCount_management ("PWFiberOptic_lyr")[0]


 arcpy.CopyFeatures_management("PWFiberOptic_lyr", WorkingPWFiberOpticCableFC)

 CopiedPWFiberOpticCount = arcpy.GetCount_management (WorkingPWFiberOpticCableFC)[0]

 if(ExtractedPWFiberOpticCount == CopiedPWFiberOpticCount):
     print("Successfully Copied ALL Public Works Fiber Optic Features into Working File Geodatabse!")
     WriteToLog("Successfully Copied ALL Public Works Fiber Optic Features into Working File Geodatabse!")
 else:
     print("There was a problem generating the Fiber Optic Features From the Disaster Recovery Source Data")
     WriteToLog("There was a problem generating the Fiber Optic Features From the Disaster Recovery Source Data")
     ProblemFound = True

 print ("Extracted " + str(ExtractedPWFiberOpticCount)+ " Public Works Fiber Optic Cable Features Successfully!")
 WriteToLog("Extracted " + str(ExtractedPWFiberOpticCount)+ " Public Works Fiber Optic Cable Features Successfully!")

 #Add to Extraction List

 ExtractionList.append(WorkingPWFiberOpticCableFC)


#Create PrimaryUGLineSection Feature Layer (No Filter To Be Applied)

if(ProblemFound == False):

 OriginalPrimaryUGLineSectionFC = DisasterElectricGDB+"\PrimaryUGLineSection"
 WorkingPrimaryUGLineSectionFC = WorkingFileGDB + "\PrimaryUGLineSection"

 arcpy.MakeFeatureLayer_management(OriginalPrimaryUGLineSectionFC, "PrimaryUGLineSection_lyr")


 ExtractedPrimaryUGLineSectionCount = arcpy.GetCount_management ("PrimaryUGLineSection_lyr")[0]


 arcpy.CopyFeatures_management("PrimaryUGLineSection_lyr", WorkingPrimaryUGLineSectionFC)

 CopiedPrimaryUGLineSectionFCCount = arcpy.GetCount_management (WorkingPrimaryUGLineSectionFC)[0]

 if(ExtractedPrimaryUGLineSectionCount == CopiedPrimaryUGLineSectionFCCount):
     print("Successfully Copied ALL Primary Underground Features into Working File Geodatabase!")
     WriteToLog("Successfully Copied ALL Primary Underground Features into Working File Geodatabase!")
 else:
     print("There was a problem generating the Primary Underground Features From the Disaster Recovery Source Data")
     WriteToLog("There was a problem generating the Primary Underground Features From the Disaster Recovery Source Data")
     ProblemFound = True

 print ("Extracted " + str(ExtractedPrimaryUGLineSectionCount)+ " City PrimaryUGLineSection Features Successfully!")
 WriteToLog("Extracted " + str(ExtractedPrimaryUGLineSectionCount)+ " City PrimaryUGLineSection Features Successfully!")

 #Add to Extraction List

 ExtractionList.append(WorkingPrimaryUGLineSectionFC)

if(ProblemFound == False):

 #Create SecondaryUGLineSection Feature Layer (No Filter To Be Applied)

 OriginalSecondaryUGLineSectionFC = DisasterElectricGDB+"\SecondaryUGLineSection"
 WorkingSecondaryUGLineSectionFC = WorkingFileGDB + "\SecondaryUGLineSection"


 arcpy.MakeFeatureLayer_management(OriginalSecondaryUGLineSectionFC, "SecondaryUGLineSection_lyr")


 ExtractedSecondaryUGLineSectionCount = arcpy.GetCount_management ("SecondaryUGLineSection_lyr")[0]




 arcpy.CopyFeatures_management("SecondaryUGLineSection_lyr", WorkingSecondaryUGLineSectionFC)

 CopiedSecondaryUGLineSectionFCCount = arcpy.GetCount_management (WorkingSecondaryUGLineSectionFC)[0]

 if(ExtractedSecondaryUGLineSectionCount == CopiedSecondaryUGLineSectionFCCount):
     print("Successfully Copied ALL Secondary Underground Features into Working File Geodatabase!")
     WriteToLog("Successfully Copied ALL Secondary Underground Features into Working File Geodatabase!")
 else:
     print("There was a problem generating the Secondary Underground Features From the Disaster Recovery Source Data")
     WriteToLog("There was a problem generating the Secondary Underground Features From the Disaster Recovery Source Data")
     ProblemFound = True

 print ("Extracted " + str(ExtractedSecondaryUGLineSectionCount)+ " City SecondaryUGLineSection Features Successfully!")
 WriteToLog("Extracted " + str(ExtractedSecondaryUGLineSectionCount)+ " City SecondaryUGLineSection Features Successfully!")

 #Add to Extraction List

 ExtractionList.append(WorkingSecondaryUGLineSectionFC)

if(ProblemFound == False):


 #Create Sanitary Sewer Feature Layer

 OriginalSanitarySewerFC = DisasterCityFileGDB+"\PW_sewer\San_Lines"
 WorkingSanitarySewerFC = WorkingFileGDB + "\San_Lines"

 arcpy.MakeFeatureLayer_management(OriginalSanitarySewerFC, "OriginalSanitarySewer_lyr")

 arcpy.SelectLayerByAttribute_management("OriginalSanitarySewer_lyr", "NEW_SELECTION", 
                                          "Owner = 'City' OR Owner IS NULL")


 ExtractedSanitarySewerCount = arcpy.GetCount_management ("OriginalSanitarySewer_lyr")[0]


 arcpy.CopyFeatures_management("OriginalSanitarySewer_lyr", WorkingSanitarySewerFC)

 CopiedSanitarySewerFCCount = arcpy.GetCount_management (WorkingSanitarySewerFC)[0]

 if(ExtractedSanitarySewerCount == CopiedSanitarySewerFCCount):
     print("Successfully Copied ALL Sanitary Sewer Features into Working File Geodatabase!")
     WriteToLog("Successfully Copied ALL Sanitary Sewer Features into Working File Geodatabase!")
 else:
     print("There was a problem generating the Sanitary Sewer Features From the Disaster Recovery Source Data")
     WriteToLog("There was a problem generating the Sanitary Sewer Features From the Disaster Recovery Source Data")
     ProblemFound = True



 print ("Extracted " + str(ExtractedSanitarySewerCount)+ " City San_Lines Features Successfully!")
 WriteToLog("Extracted " + str(ExtractedSanitarySewerCount)+ " City San_Lines Features Successfully!")


 #Add to Extraction List

 ExtractionList.append(WorkingSanitarySewerFC)


#Create Lateral Lines Feature Layer

if(ProblemFound == False):

 OriginalLateralLineFC = DisasterCityFileGDB+"\Water_Network\wLateralLine"
 WorkingLateralLineFC = WorkingFileGDB + "\wLateralLine"

 arcpy.MakeFeatureLayer_management(OriginalLateralLineFC, "OriginalLateralLine_lyr")

 arcpy.SelectLayerByAttribute_management("OriginalLateralLine_lyr", "NEW_SELECTION", 
                                          "Private <> 'Yes'")


 ExtractedLateralLineCount = arcpy.GetCount_management ("OriginalLateralLine_lyr")[0]


 arcpy.CopyFeatures_management("OriginalLateralLine_lyr", WorkingLateralLineFC)

 CopiedLateralLineFCCount = arcpy.GetCount_management (WorkingLateralLineFC)[0]



 if(ExtractedLateralLineCount == CopiedLateralLineFCCount):
     print("Successfully Copied ALL Lateral Line Features into Working File Geodatabase!")
     WriteToLog("Successfully Copied ALL Lateral Line Features into Working File Geodatabase!")
 else:
     print("There was a problem generating the Lateral Line Features From the Disaster Recovery Source Data")
     WriteToLog("There was a problem generating the Lateral Line Features From the Disaster Recovery Source Data")
     ProblemFound = True

 print ("Extracted " + str(ExtractedLateralLineCount)+ " City LateralLine Features Successfully!")
 WriteToLog("Extracted " + str(ExtractedLateralLineCount)+ " City LateralLine Features Successfully!")

 #Add to Extraction List

 ExtractionList.append(WorkingLateralLineFC)


#Create Pressurized Mains Feature Layer

if(ProblemFound == False):


 OriginalPressurizedMainsFC = DisasterCityFileGDB+"\Water_Network\wPressurizedMain"
 WorkingPressurizedMainsFC = WorkingFileGDB + "\wPressurizedMain"


 arcpy.MakeFeatureLayer_management(OriginalPressurizedMainsFC, "wPressurizedMain_lyr")

 arcpy.SelectLayerByAttribute_management("wPressurizedMain_lyr", "NEW_SELECTION", 
                                          "Owner='City' OR Owner IS NULL")


 ExtractedPressurizedMainCount = arcpy.GetCount_management ("wPressurizedMain_lyr")[0]


 arcpy.CopyFeatures_management("wPressurizedMain_lyr", WorkingPressurizedMainsFC)

 CopiedPressurizedMainsFCCount = arcpy.GetCount_management (WorkingPressurizedMainsFC)[0]

 if(ExtractedPressurizedMainCount == CopiedPressurizedMainsFCCount):
     print("Successfully Copied ALL Pressurized Main Features into Working File Geodatabse!")
     WriteToLog("Successfully Copied ALL Pressurized Main Features into Working File Geodatabse!")

 else:
     print("There was a problem generating the Pressurized Main Features From the Disaster Recovery Source Data")
     WriteToLog("There was a problem generating the Pressurized Main Features From the Disaster Recovery Source Data")
     ProblemFound = True



 print ("Extracted " + str(ExtractedPressurizedMainCount)+ " City Pressurized Main Features Successfully!")
 WriteToLog("Extracted " + str(ExtractedPressurizedMainCount)+ " City Pressurized Main Features Successfully!")

 #Add to Extraction List

 ExtractionList.append(WorkingPressurizedMainsFC)

if(ProblemFound == False):

 print("*********************************************")
 print("       Generating Intial Utility Buffers.....")
 print("*******************************************\n")

BufferResultList = []

FCCount = 0
for FC in ExtractionList:
     count = arcpy.GetCount_management(FC)[0]
     lastindex = FC.rfind('\\')
     FCCount = FCCount+ 1

     print("Buffering " + str(count) + " " + FC[lastindex+1:] + " Features...")

     BufferFC = arcpy.Buffer_analysis(FC, WorkingFileGDB+"\\"+FC[lastindex+1:] + "_Buffer", "100 Feet", "FULL", 
                       "ROUND", "ALL", "","PLANAR")

     print ("Buffer Completed for " + str(FC[lastindex+1:]) + " Feature Class")
     WriteToLog("Buffer Completed for " + str(FC[lastindex+1:]) + " Feature Class")

     #Add it to the Buffer Result List in Prep for Final Merge

    

     BufferResultList.append(BufferFC)

    
 #Loop through the Buffer Results and Merge Them

print("Combining Buffer Polygons into Single Layer for Processing...\n")
WriteToLog("Combining Buffer Polygons into Single Layer for Processing...")
Fiber_Buffer = "C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\Fiber_Buffer"
FiberOpticCable_Buffer = "C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\FiberOpticCable_Buffer"
PrimaryUGLineSection_Buffer = "C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\PrimaryUGLineSection_Buffer"
PW_FiberOpticCable_Buffer = "C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\PW_FiberOpticCable_Buffer"
San_Lines_Buffer = "C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\San_Lines_Buffer"
SecondaryUGLineSection_Buffer = "C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\SecondaryUGLineSection_Buffer"
wLateralLine_Buffer = "C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\wLateralLine_Buffer"
wPressurizedMain_Buffer = "C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\wPressurizedMain_Buffer"
MergedBuffers = "C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\MergedBuffers"



#Include a script parameter to also generate two additional buffer outputs
#1. Electric/Fiber
#2. Water/Sewer

if(CreateEF_WS_Buffers == True):
   arcpy.Merge_management(inputs="Fiber_Buffer;FiberOpticCable_Buffer;PW_FiberOpticCable_Buffer;PrimaryUGLineSection_Buffer;SecondaryUGLineSection_Buffer", output="C:/OneCallBufferCreation/OneCallBuffers.gdb/EF_Buffers", field_mappings='SHAPE_Length "SHAPE_Length" false true true 8 Double 0 0 ,First,#,Fiber_Buffer,SHAPE_Length,-1,-1,FiberOpticCable_Buffer,Shape_Length,-1,-1,PW_FiberOpticCable_Buffer,Shape_Length,-1,-1,PrimaryUGLineSection_Buffer,Shape_Length,-1,-1,SecondaryUGLineSection_Buffer,Shape_Length,-1,-1;SHAPE_Area "SHAPE_Area" false true true 8 Double 0 0 ,First,#,Fiber_Buffer,SHAPE_Area,-1,-1,FiberOpticCable_Buffer,Shape_Area,-1,-1,PW_FiberOpticCable_Buffer,Shape_Area,-1,-1,PrimaryUGLineSection_Buffer,Shape_Area,-1,-1,SecondaryUGLineSection_Buffer,Shape_Area,-1,-1')
   arcpy.Merge_management(inputs="San_Lines_Buffer;wPressurizedMain_Buffer;wLateralLine_Buffer", output="C:/OneCallBufferCreation/OneCallBuffers.gdb/WS_Buffers", field_mappings='Shape_Length "Shape_Length" false true true 8 Double 0 0 ,First,#,San_Lines_Buffer,Shape_Length,-1,-1,wPressurizedMain_Buffer,Shape_Length,-1,-1,wLateralLine_Buffer,Shape_Length,-1,-1;Shape_Area "Shape_Area" false true true 8 Double 0 0 ,First,#,San_Lines_Buffer,Shape_Area,-1,-1,wPressurizedMain_Buffer,Shape_Area,-1,-1,wLateralLine_Buffer,Shape_Area,-1,-1')
 
# Create Merged Buffers for Missouri One Call
arcpy.Merge_management("C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\Fiber_Buffer;C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\FiberOpticCable_Buffer;C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\PrimaryUGLineSection_Buffer;C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\PW_FiberOpticCable_Buffer;C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\San_Lines_Buffer;C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\SecondaryUGLineSection_Buffer;C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\wLateralLine_Buffer;C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\wPressurizedMain_Buffer", MergedBuffers, "SHAPE_Length \"SHAPE_Length\" false true true 8 Double 0 0 ,First,#,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\Fiber_Buffer,SHAPE_Length,-1,-1,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\FiberOpticCable_Buffer,Shape_Length,-1,-1,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\PrimaryUGLineSection_Buffer,Shape_Length,-1,-1,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\PW_FiberOpticCable_Buffer,Shape_Length,-1,-1,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\San_Lines_Buffer,Shape_Length,-1,-1,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\SecondaryUGLineSection_Buffer,Shape_Length,-1,-1,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\wLateralLine_Buffer,Shape_Length,-1,-1,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\wPressurizedMain_Buffer,Shape_Length,-1,-1;SHAPE_Area \"SHAPE_Area\" false true true 8 Double 0 0 ,First,#,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\Fiber_Buffer,SHAPE_Area,-1,-1,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\FiberOpticCable_Buffer,Shape_Area,-1,-1,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\PrimaryUGLineSection_Buffer,Shape_Area,-1,-1,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\PW_FiberOpticCable_Buffer,Shape_Area,-1,-1,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\San_Lines_Buffer,Shape_Area,-1,-1,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\SecondaryUGLineSection_Buffer,Shape_Area,-1,-1,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\wLateralLine_Buffer,Shape_Area,-1,-1,C:\\OneCallBufferCreation\\OneCallBuffers.gdb\\wPressurizedMain_Buffer,Shape_Area,-1,-1")
print("Process Complete!\n")


#Copy the Modified Snow Grid into Working File GDB

print("Gathering the Snow Grid for Page Name Assignment....")
ModifiedSnowGrid = "S:\WL\MarkRees\OneCallBufferCreation\All_Utilities_Buffers.gdb\Modified_Snow_Grid"
arcpy.CopyFeatures_management(ModifiedSnowGrid, WorkingFileGDB+"\Modified_Snow_Grid")
print("Modified Snow Grid Copied Successfully!...")
WriteToLog("Modified Snow Grid Copied Successfully!...")

#Merge the Buffers

DissolvedBuffers = WorkingFileGDB+"\DissolvedBuffers"
print("Dissolving Buffers into One Polygon....")
WriteToLog("Dissolving Buffers into One Polygon....")
arcpy.Buffer_analysis(MergedBuffers, DissolvedBuffers, "1 Feet", "FULL", "ROUND", "ALL", "", "PLANAR")
print("Dissolve Process Completed Successfully!")


#Loop through the Input Feature Classes and Check if ALL Features are found within a Buffer

for FC in ExtractionList:
    print("Selecting Features From Feature Class " + FC + " Inside Buffer Polygons...")
    WriteToLog("Selecting Features From Feature Class " + FC + " Inside Buffer Polygons...")
    arcpy.MakeFeatureLayer_management(FC,"FLayer")
    NumFeatures = int(arcpy.GetCount_management("FLayer")[0])
    arcpy.SelectLayerByLocation_management("FLayer", "COMPLETELY_WITHIN", DissolvedBuffers, "", "NEW_SELECTION", "NOT_INVERT")
    NumInsideBuffer = arcpy.GetCount_management("FLayer")

    print("The Number of Features in " + FC + " are : " + str(NumFeatures) + " The Number of Features Within Buffer were " + str(int(NumInsideBuffer[0])) )
    WriteToLog("The Number of Features in " + FC + " are : " + str(NumFeatures) + " The Number of Features Within Buffer were " + str(int(NumInsideBuffer[0])))


#Create a Feature Dataset to Hold the Exploded Buffer Feature Classes

print("Gathering Spatial Reference Information...")
destination_spatialref = arcpy.CreateSpatialReference_management("NAD 1983 StatePlane Missouri Central FIPS 2402 (US Feet)")
arcpy.CreateFeatureDataset_management("C:/OneCallBufferCreation/OneCallBuffers.gdb", "OutputBuffers", destination_spatialref)
print("Spatial Reference Information Applied to Buffer Feature Dataset...")
WriteToLog("Spatial Reference Information Applied to Buffer Feature Dataset...")

#Create a Feature Dataset to Hold the Final Buffer Feature Classes

print("Gathering Spatial Reference Information...")
WriteToLog("Gathering Spatial Reference Information...")
destination_spatialref = arcpy.CreateSpatialReference_management("NAD 1983 StatePlane Missouri Central FIPS 2402 (US Feet)")
arcpy.CreateFeatureDataset_management("C:/OneCallBufferCreation/OneCallBuffers.gdb", "FinalBuffers", destination_spatialref)
print("Spatial Reference Information Applied to Buffer Feature Dataset...")
WriteToLog("Spatial Reference Information Applied to Buffer Feature Dataset...")

#Add the MAPPREF field to the Dissolved Buffers Feature Class

arcpy.AddField_management(DissolvedBuffers, "MAPPREF", "TEXT", "", "", "29", "", "NULLABLE", "NON_REQUIRED", "")



# #Perform the Split Polygons Using the Modified Snow Grid

print("Creating Individual Buffers Based on Snow Grid Position....")
WriteToLog("Creating Individual Buffers Based on Snow Grid Position....")
SnowGridRef = WorkingFileGDB+"\Modified_Snow_Grid"
arcpy.Split_analysis(in_features=DissolvedBuffers, split_features=SnowGridRef, split_field="PageName", out_workspace="C:/OneCallBufferCreation/OneCallBuffers.gdb/OutputBuffers", cluster_tolerance="")
print("Process Complete!..")
WriteToLog("Process Complete!..")

#Assign Page Name to the Buffer Feature Classes

env.workspace = "C:/OneCallBufferCreation/OneCallBuffers.gdb/OutputBuffers"
arcpy.env.overwriteOutput = True

path = "C:\\OneCallShapeFiles\\"
if os.path.exists(path) == True:
     shutil.rmtree(path)
     os.mkdir(path)
else:
      os.mkdir(path)

#Create FinalTemp Feature Class

print("Writing Output Shapefiles....")
WriteToLog("Writing Output Shapefiles....")
print("Transferring PageName Field Values....")
WriteToLog("Transferring PageName Field Values....")
FCList = arcpy.ListFeatureClasses()
count = 0
appendcount = 0

#Create the Feature Class Template
print ("Generating Template Feature Class.....")
WriteToLog("Generating Template Feature Class.....")
arcpy.ImportXMLWorkspaceDocument_management(target_geodatabase="C:/OneCallBufferCreation/OneCallBuffers.gdb", in_file="S:\\WL\\MarkRees\\OneCallBufferCreation\\SHAPEFILETEMPLATE.XML", import_type="SCHEMA_ONLY", config_keyword="")
print ("Template Feature Class Generated Successfully!")
WriteToLog("Template Feature Class Generated Successfully!")


for BuffFC in FCList:
     A1 = BuffFC
     count = count + 1
     appendcount = appendcount + 1
    
    

     # Process: Spatial Join
     outfc = BuffFC+ "_Final"
     print("Performing Identity " + str(appendcount)+ " to Transfer PageName....")
     WriteToLog("Performing Identity " + str(appendcount)+ " to Transfer PageName....")
     arcpy.Identity_analysis(A1,SnowGridRef, outfc,"ALL", cluster_tolerance="", relationship="NO_RELATIONSHIPS")
     print("Identity Operation Successfull!...")
     WriteToLog("Identity Operation Successfull!...")
                            
    
     #Calculate MAPPREF field to match PageName

     arcpy.CalculateField_management(outfc, "MAPPREF", "!PageName!", "PYTHON_9.3", "#")


     #Append into the Template Feature Class
    
     arcpy.Append_management(outfc, "C:\OneCallBufferCreation\OneCallBuffers.gdb\TempFC","NO_TEST")
    
     print(str(appendcount) + " Buffer Polygon Features Appended into Template Feature Class Succesffully....")
     WriteToLog(str(appendcount) + " Buffer Polygon Features Appended into Template Feature Class Succesffully....")


#Rename the fields Before Converting to Shapefile...

import arcpy

TempFC = "C:\OneCallBufferCreation\OneCallBuffers.gdb\TempFC"



#Rename the fields Before Converting to Shapefile...

fieldlist = arcpy.ListFields(TempFC)


for field in fieldlist:
     fieldname = str(field.name)
    
     fieldlength = len(fieldname)
     if fieldlength >= 10 and 'PageName' in fieldname:
         newname = fieldname.replace("PageName","Page")
         arcpy.AlterField_management(TempFC, fieldname, newname, newname)
print ("Fields Renamed to Shapefile Standard....")
WriteToLog("Fields Renamed to Shapefile Standard....")

#Convert to Final Shapefile For Delivery
print("Converting Feature Class to Delivery Shapefile...")
WriteToLog("Converting Feature Class to Delivery Shapefile...")


#Define Spatial Reference
spatial_ref = arcpy.Describe(TempFC).spatialReference
arcpy.DefineProjection_management(TempFC, spatial_ref)


arcpy.FeatureClassToShapefile_conversion(TempFC,"C:\OneCallBufferCreation")
print ("Delivery Shapefile Generated....")
WriteToLog("Delivery Shapefile Generated....")


#Repair Geometry (Do not delete null values option

print ("Repairing Geometry.....")
arcpy.RepairGeometry_management(in_features="C:\OneCallBufferCreation\TempFC.shp", delete_null="KEEP_NULL")
WriteToLog("Repairing Geometry.....")
  
# #Add Spatial Index

print ("Buidling Spatial Index....")
WriteToLog("Buidling Spatial Index....")
arcpy.AddSpatialIndex_management("C:\OneCallBufferCreation\TempFC.shp")


#Perform Check Geometry

print ("Checking Geometry for Errors....")
WriteToLog("Checking Geometry for Errors....")
CheckTable = "C:/OneCallBufferCreation/OneCallBuffers.gdb/GeometryCheckResult"
if os.path.exists(CheckTable) == True:
     os.remove(CheckTable)
arcpy.CheckGeometry_management(in_features="C:\OneCallBufferCreation\TempFC.shp", out_table="C:/OneCallBufferCreation/OneCallBuffers.gdb/GeometryCheckResult")


#Check the number of rows in the Check Geometry Result

result = arcpy.GetCount_management(CheckTable)
rowcount = int(result.getOutput(0))
if rowcount > 0:
     print ("Geometry Issues Discovered in Final Output...Please Review")
     WriteToLog("Geometry Issues Discovered in Final Output...Please Review")
else:
     print ("Geometry Check Successfull! Final Output ZIP OK for Delivery!")
     WriteToLog("Geometry Check Successfull! Final Output ZIP OK for Delivery!")

#Define Projection (Ensure PRJ associated with ShapeFile

print("Associating Correct Projection to Shapefile....")
WriteToLog("Associating Correct Projection to Shapefile....")
arcpy.DefineProjection_management(in_dataset="C:\\OneCallBufferCreation\\TempFC.shp", coor_system="PROJCS['NAD_1983_StatePlane_Missouri_Central_FIPS_2402_Feet',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',1640416.666666667],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-92.5],PARAMETER['Scale_Factor',0.9999333333333333],PARAMETER['Latitude_Of_Origin',35.83333333333334],UNIT['Foot_US',0.3048006096012192]]")




print("Creating ZIP File for Delivery..." ) 
WriteToLog("Creating ZIP File for Delivery...")


#Rename the Shapefile before Compression to ZIP
print("Renaming Shapefile Before Final Packaging...")
WriteToLog("Renaming Shapefile Before Final Packaging...")
arcpy.Rename_management("C:\\OneCallBufferCreation\\TempFC.shp","UtilityBuffer.shp")
print("Rename Successfull!")
WriteToLog("Rename Successfull!")

zippath = "C:\\OneCallBufferCreation\\UtilityBuffers.zip"
if os.path.exists(zippath) == True:
     os.remove(zippath)
zipObj = ZipFile("C:\\OneCallBufferCreation\\UtilityBuffers.zip", 'w')
# Add multiple files to the zip
zipObj.write('C:\\OneCallBufferCreation\\UtilityBuffer.cpg')
zipObj.write('C:\\OneCallBufferCreation\\UtilityBuffer.dbf')
zipObj.write('C:\\OneCallBufferCreation\\UtilityBuffer.prj')
zipObj.write('C:\\OneCallBufferCreation\\UtilityBuffer.shp')
zipObj.write('C:\\OneCallBufferCreation\\UtilityBuffer.shp.xml')
zipObj.write('C:\\OneCallBufferCreation\\UtilityBuffer.shx')
                 
# close the Zip File
zipObj.close()

WriteToLog("Final Output Buffer Shapefile ZIP Generated Successfully!..")
print("Final Output Buffer Shapefile ZIP Generated Successfully!..")
