import outreach_analytics
from parsons import Table


def test_get_target_name():
    input = ["4be2fd069a10ec44b275bd4b71466e17"]
    output = "Mark Kelly"

    assert outreach_analytics.get_target_name(input) == output


def test_transform_outreaches():
    input = [
        {
            "outreach_id": "10591961",
            "created_date": "1619106357",
            "modified_date": "1619106357",
            "action_date": "1619106357",
            "type": "call",
            "targets": [
                "TESTMODE-f027b94c26b27b1f34fc08b786514f74-dd9e0d50fc889a3601d21001f6711147",
                "TESTMODE-f027b94c26b27b1f34fc08b786514f74-6b2e6177617cacfdc31111f91db4abd0",
                "TESTMODE-f027b94c26b27b1f34fc08b786514f74-e5aed8a6d4411d252370aa922bbc828b",
            ],
            "person": {
                "postal_code": "02906",
                "given_name": "Matthew",
                "email": ["matthewmellea@gmail.com"],
                "phone": ["(650) 946-7412"],
                "family_name": "Mellea",
            },
            "subject": None,
            "message": None,
            "duration": None,
            "metadata": {
                "browser": "Chrome",
                "device": "Desktop",
                "district": ["RI", "RI", "RI District 1"],
                "mobile": "false",
                "parent url": "https://engage.newmode.net/node/34935",
                "party": ["Democrat", "Democrat", "Democrat"],
                "platform": "MacOSX",
                "source type": "EMBED",
                "testmode": "on",
                "call caller number": " 12029027870",
                "call destination number": " 16509467412",
                "overall call duration": "105",
                "overall call end time": "1619106462",
                "call status": "completed",
                "call hangup reason": "User hung up phone",
            },
            "formdata": {"click2call": "436330"},
        }
    ]

    output = [
        {
            "outreach_id": 10591961,
            "created_date": "2021-04-22",
            "target_names": "Jack Reed, Sheldon Whitehouse, David Cicilline",
            "name": "Matthew Mellea",
            "phone": "(650) 946-7412",
        }
    ]

    assert outreach_analytics.transform_outreaches(input) == output


def test_group_by_and_count():
    input = [
        {
            "outreach_id": 10591961,
            "created_date": "2021-04-22",
            "target_names": "Jack Reed, Sheldon Whitehouse, David Cicilline",
            "name": "Matthew Mellea",
            "phone": ["(650) 946-7412"],
        },
        {
            "outreach_id": 10592577,
            "created_date": "2021-04-22",
            "target_names": "Jack Reed, Sheldon Whitehouse, David Cicilline",
            "name": "Matthew Mellea",
            "phone": ["(650) 946-7412"],
        },
        {
            "outreach_id": 10613970,
            "created_date": "2021-04-23",
            "target_names": "Kirsten E. Gillibrand, Charles E. Schumer, Yvette D. Clarke",
            "name": "Aracely Jimenez-Hudis",
            "phone": ["(347) 204-7223"],
        },
    ]

    output = Table(
        [
            {"created_date": "2021-04-22", "num_calls": 2},
            {"created_date": "2021-04-23", "num_calls": 1},
        ]
    )

    assert outreach_analytics.group_by_and_count(input, "created_date") == output
