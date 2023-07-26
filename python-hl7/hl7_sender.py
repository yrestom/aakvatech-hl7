# Using the third party `aiorun` instead of the `asyncio.run()` to avoid
# boilerplate.
import aiorun
import asyncio

import hl7
from hl7.mllp import open_hl7_connection

print("started...")


async def main():
    message = """MSH|^~\&|BC-5380|Mindray|||20210202151447||ORU^R01|87|P|2.3.1||||||UNICODE
PID|1||||
PV1|1||
OBR|1||155|00001^Automated Count^99MRC|||20210202151339|||||||||||||||||HM||||||||Service Engineer
OBX|1|IS|08001^Take Mode^99MRC||C||||||F
OBX|2|IS|08002^Blood Mode^99MRC||W||||||F
OBX|3|IS|08003^Test Mode^99MRC||CBC+DIFF||||||F
OBX|4|IS|01002^Ref Group^99MRC||General||||||F
OBX|5|NM|6690-2^WBC^LN||3.91|10*9/L|4.00-10.00|L|||F
OBX|6|NM|704-7^BAS#^LN||0.03|10*9/L|0.00-0.10|N~A|||F
OBX|7|NM|706-2^BAS%^LN||0.8|%|0.0-1.0|N~A|||F
OBX|8|NM|751-8^NEU#^LN||2.31|10*9/L|2.00-7.00|N~A|||F
OBX|9|NM|770-8^NEU%^LN||59.1|%|50.0-70.0|N~A|||F
OBX|10|NM|711-2^EOS#^LN||0.16|10*9/L|0.02-0.50|N~A|||F
OBX|11|NM|713-8^EOS%^LN||4.0|%|0.5-5.0|N~A|||F
OBX|12|NM|731-0^LYM#^LN||1.27|10*9/L|0.80-4.00|N|||F
OBX|13|NM|736-9^LYM%^LN||32.4|%|20.0-40.0|N|||F
OBX|14|NM|742-7^MON#^LN||0.14|10*9/L|0.12-1.20|N~A|||F
OBX|15|NM|5905-5^MON%^LN||3.7|%|3.0-12.0|N~A|||F
OBX|16|NM|26477-0^*ALY#^LN||0.00|10*9/L|0.00-0.20|N|||F
OBX|17|NM|13046-8^*ALY%^LN||0.1|%|0.0-2.0|N|||F
OBX|18|NM|10000^*LIC#^99MRC||0.00|10*9/L|0.00-0.20|N~A|||F
OBX|19|NM|10001^*LIC%^99MRC||0.0|%|0.0-2.5|N~A|||F
OBX|20|NM|789-8^RBC^LN||4.84|10*12/L|3.50-5.50|N|||F
OBX|21|NM|718-7^HGB^LN||13.8|g/dL|11.0-16.0|N|||F
OBX|22|NM|787-2^MCV^LN||89.0|fL|80.0-100.0|N|||F
OBX|23|NM|785-6^MCH^LN||28.4|pg|27.0-34.0|N|||F
OBX|24|NM|786-4^MCHC^LN||31.9|g/dL|32.0-36.0|L|||F
OBX|25|NM|788-0^RDW-CV^LN||12.5|%|11.0-16.0|N|||F
OBX|26|NM|21000-5^RDW-SD^LN||46.6|fL|35.0-56.0|N|||F
OBX|27|NM|4544-3^HCT^LN||0.431||0.370-0.540|N|||F
OBX|28|NM|777-3^PLT^LN||204|10*9/L|100-300|N|||F
OBX|29|NM|32623-1^MPV^LN||8.8|fL|6.5-12.0|N|||F
OBX|30|NM|32207-3^PDW^LN||16.0||9.0-17.0|N|||F
OBX|31|NM|10002^PCT^99MRC||0.179|%|0.108-0.282|N|||F
OBX|32|IS|17790-7^WBC Left Shift?^LN||T||||||F
OBX|33|IS|34165-1^Imm Granulocytes?^LN||T||||||F
OBX|34|NM|15001^WBC Histogram. Left Line^99MRC||12||||||F
OBX|35|NM|15002^WBC Histogram. Right Line^99MRC||72||||||F
OBX|36|NM|15003^WBC Histogram. Middle Line^99MRC||40||||||F
OBX|37|NM|15004^WBC Histogram. Meta Length^99MRC||2||||||F
OBX|38|ED|15000^WBC Histogram. Binary^99MRC||^Application^Octet-stream^Base64^AAAAAAAAAAAAAAAAAAAAAAAAANUBCgFAAeAD9QvgD/8P/w//D/8P/w//D/8P/w//D/8NwAjABuAF1QQqAoABqgFAAGoAagCgANUAoABqAGoANQA1AAAAAAA1ADUANQA1AAAAAAA1ADUAAAA1AAAAAAAAAAAAAAAAAAAANQA1ADUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANQA1AAAAAAAAAAAAAAAAAAAANQAAAAAANQA1AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==||||||F
OBX|39|NM|15051^RBC Histogram. Left Line^99MRC||29||||||F
OBX|40|NM|15052^RBC Histogram. Right Line^99MRC||152||||||F
OBX|41|NM|15053^RBC Histogram. Binary Meta Length^99MRC||2||||||F
OBX|42|ED|15050^RBC Histogram. Binary^99MRC||^Application^Octet-stream^Base64^AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQABAAEAAgADAAQABgAIAAwAEAAVABwAJQAwADwASgBbAGsAfgCRAKMAtQDFANYA4wDuAPYA+wD/AP0A9wDwAOUA2ADJALkAqwCaAIsAewBsAGAAUgBIAD4ANgAuACcAIQAbABYAEgAOAAsACQAHAAYABQAEAAQAAwADAAIAAgACAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAgABAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAwADAAMAAwADAAMAAwADAAIAAgACAAIAAgACAAEAAQABAAEAAQABAAEAAQABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=||||||F
OBX|43|NM|15111^PLT Histogram. Left Line^99MRC||3||||||F
OBX|44|NM|15112^PLT Histogram. Right Line^99MRC||47||||||F
OBX|45|NM|15113^PLT Histogram. Binary Meta Length^99MRC||2||||||F
OBX|46|ED|15100^PLT Histogram. Binary^99MRC||^Application^Octet-stream^Base64^AAAAAAAAABcAPABsAKUAywDmAPcA/wD/APsA7QDiANIAwACwAJsAhQBzAGIAUwBHADwAMwAuACoAJQAhACAAHAAaABgAEwARABEAEAAQAA4ADAAMAAwADAAMAAwACgAIAAgABwAIAAgACgAMAAwADAAMAAwADAAQABEAFwAeACU=||||||F"""

    # Open the connection to the HL7 receiver.
    # Using wait_for is optional, but recommended so
    # a dead receiver won't block you for long

    hl7_reader, hl7_writer = await asyncio.wait_for(open_hl7_connection("127.0.0.1", 2550), timeout=10,)
    hl7_message = hl7.parse(message)
    # Write the HL7 message, and then wait for the writer
    # to drain to actually send the message
    hl7_writer.writemessage(hl7_message)
    await hl7_writer.drain()
    print(f'Sent message\n {hl7_message}'.replace('\r', '\n'))
    # Now wait for the ACK message from the receiever
    hl7_ack = await asyncio.wait_for(
        hl7_reader.readmessage(),
        timeout=10
    )
    print(f'Received ACK\n {hl7_ack}'.replace('\r', '\n'))

aiorun.run(main(), stop_on_unhandled_errors=True)
