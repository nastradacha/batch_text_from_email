import requests
from bs4 import BeautifulSoup as Bs
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd

email = "*****@gmail.com"
pas = "************"


def phone_number_from_csv(path_to_csv):
    """

    :param path_to_csv:
    :return: list of phone numbers pulled from csv file
    """
    csv_file = fr"{path_to_csv}"
    df = pd.read_csv(csv_file)
    return list(df["Phone"])


def carrier(ph_number):
    headers = {
        "authority": "www.numlookup.com",
        "accept": "*/*",
        "x-requested-with": "XMLHttpRequest",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/89.0.4389.128 Safari/537.36 Edg/89.0.774.77",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://www.numlookup.com",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://www.numlookup.com/",
        "accept-language": "en-US,en;q=0.9",
        "cookie": "_ga=GA1.2.2080482850.1618853739; _gid=GA1.2.404720638.1618853739; "
        "__gads=ID=b0b1c0d0f747b43a-228dee0a44c70043:T=1618853738:RT=1618853738:S"
        "=ALNI_MbbIBNAYfkmDOyVZ9Dcl7NLdIWb6w; "
        "php_session=a^%^3A5^%^3A^%^7Bs^%^3A10^%^3A^%^22session_id^%^22^%^3Bs^%^3A32^%^3A"
        "^%^221ca1a122a8ec9d00370b9f25f30b81b8^%^22^%^3Bs^%^3A10^%^3A^%^22ip_address^%^22^%^3Bs^%^3A12^%^3A"
        "^%^22208.54.104.5^%^22^%^3Bs^%^3A10^%^3A^%^22user_agent^%^22^%^3Bs^%^3A120^%^3A^%^22Mozilla^%^2F5"
        ".0+^%^28Windows+NT+10.0^%^3B+Win64^%^3B+x64^%^29+AppleWebKit^%^2F537.36+^%^28KHTML^%^2C+like+Gecko"
        "^%^29+Chrome^%^2F89.0.4389.128+Safari^%^2F537.36+Edg^%^2F^%^22^%^3Bs^%^3A13^%^3A^%^22last_activity"
        "^%^22^%^3Bi^%^3A1618853773^%^3Bs^%^3A9^%^3A^%^22user_data^%^22^%^3Bs^%^3A0^%^3A^%^22^%^22^%^3B"
        "^%^7D89d683e2eec00d127e9af981b0fe51f4d02786a8; _gat_gtag_UA_74184857_8=1",
    }
    data = {"dialNumber": f"{ph_number}", "dialCode": "+1", "country": "USA"}
    response = requests.post(
        "https://www.numlookup.com/ajax/phone_lookup", headers=headers, data=data
    )
    soup = Bs(response.text, "html.parser")
    xxx = soup.find_all("span")[1].text.split("\n")
    x = re.split("\s", xxx[0])
    range_start, range_end = x.index("by"), x.index("You")
    return " ".join(x[range_start + 1 : range_end])


def append_phone_to_gateway(number):
    """

    :param number: phone number to convert to gateway
    :return: return phone in gatewa format
    """
    if isinstance(number, list):
        lister = []
        for i in number:
            if "AT&T" in carrier(i):
                lister.append(str(i) + "@txt.att.net")
            elif "T-Mobile" in carrier(i):
                print(i)
                lister.append(str(i) + "@tmomail.net")
            elif "Sprint" in carrier(number):
                lister.append(str(i) + "@messaging.sprintpcs.com")
        return lister
    if "AT&T" in carrier(number):
        return str(number) + "@txt.att.net"
    elif "T-Mobile" in carrier(number):
        return str(number) + "@tmomail.net"
    elif "Sprint" in carrier(number):
        return str(number) + "@messaging.sprintpcs.com"


smtp = "smtp.gmail.com"
port = 587
server = smtplib.SMTP(smtp, port)
server.starttls()
phone_list = phone_number_from_csv("path")

for cc in phone_list:
    msg = MIMEMultipart()
    msg["From"] = email
    msg["To"] = append_phone_to_gateway(cc)  # sms_gateway
    msg["Subject"] = "test_email_to_phone"
    body = (
        "heyhey, It's Candy!: We'd like to offer you a coupon as a thank you for being part of our Loyalty "
        "program. SWEET, sweet, candy savings.... Get 20% off the next time you visit! https://heyitscandy.com/ "
    )
    msg.attach(MIMEText(body, "plain"))
    sms = msg.as_string()
    print(sms)
    server.login(email, pas)
    server.sendmail(email, append_phone_to_gateway(cc), sms)
server.quit()
