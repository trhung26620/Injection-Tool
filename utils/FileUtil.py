import os


class FileUtil:

    @staticmethod
    def readPayloadFromFile(filePath):
        try:
            isFileExist = os.path.isfile(filePath)
            payloadValues = []
            if isFileExist:
                fileObject = open(filePath, "r")
                for payloadValue in fileObject:
                    payloadValue = payloadValue.strip()
                    if payloadValue.strip():
                        # print(" [FileUtils] - Read line: " + payloadValue)
                        payloadValues.append(payloadValue)
                    # print("List payload: " + str(payloadValues))
                return payloadValues
            else:
                print("File not found !!!")
                return None
        except FileNotFoundError:
            print("File exception !!! ")
            fileObject.close()
            return None



