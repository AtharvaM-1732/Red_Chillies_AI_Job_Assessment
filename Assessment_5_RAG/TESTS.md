## Test cases for RAG chatbot

The document is a 16-page JBL Quantum 350 Wireless Owner's Manual, covering setup, controls, charging, specifications, pairing, and troubleshooting.

    JBL

The following test set is designed to evaluate your actual RAG pipeline, not just whether the model can answer questions from general knowledge.

## 1. Core test cases

Use these questions after uploading the PDF to your app and indexing it. The expected answers below are your reference answers for evaluating the bot.

| ID | Test question | Expected answer / key facts | PDF page |
| --- | --- | --- | --- |
| TC01 | What items are included in the box? | Headset, USB-A to USB-C charging cable, removable microphone, 2.4G USB wireless dongle, documentation, and microphone windshield foam. | 3 |
| TC02 | How long does the headset take to charge fully? | Approximately 2 hours. | 6, 12 |
| TC03 | How do I turn the headset on and off? | Slide the power switch up to turn it on and down to turn it off. The status LED glows solid white when powered on. | 8 |
| TC04 | How do I connect the headset to a PC? | Connect the 2.4G USB dongle to a USB-A port, power on the headset, then configure playback and recording devices in Windows sound settings. | 9–10 |
| TC05 | How do I manually pair the headset and dongle? | Power on the headset; hold the dongle's pairing button for more than 5 seconds until its LED flashes white quickly. Both LEDs become solid white after successful pairing. | 11 |
| TC06 | What is the headset's battery capacity and expected music playback time? | A 3.7 V / 500 mAh lithium-ion battery and up to 22 hours of music playback. | 12 |
| TC07 | What is the microphone pickup pattern? | Omnidirectional. | 12 |
| TC08 | My headset has no sound. What should I check? | Check the default sound device, device volume, successful pairing, and possible USB 3.0 interference near the dongle. | 13 |
| TC09 | Why can't my teammates hear my voice? | Check that JBL Quantum350 Wireless is the default chat recording device and that the microphone is not muted. | 14 |
| TC10 | What are the driver's size and frequency response? | 40 mm dynamic drivers; 20 Hz–20 kHz frequency response. | 12 |

    Reference: JBL Quantum 350 Wireless owner's manual.

## 2. Advanced test cases

These are particularly useful for checking whether hybrid retrieval and conversational memory are working correctly.

| ID | Test question | What it tests | Expected behavior |
| --- | --- | --- | --- |
| TC11 | How long does it take to charge, and how long can I listen to music? | Multi-fact retrieval | Returns approximately 2 hours charging and 22 hours music playback. |
| TC12 | Can I use a USB-C to USB-C cable to charge it? | Detail retrieval | Yes, the manual says it can be used, but the cable is not supplied. |
| TC13 | What should I do if the headset keeps disconnecting? | Troubleshooting retrieval | Explains that the dongle LED flashes slowly after disconnection and recommends moving the headset closer and manually pairing if necessary. |
| TC14 | What is the maximum operating temperature? | Exact specification lookup | 45 °C. |
| TC15 | Does the manual guarantee compatibility with every USB-A port? | Negative-detail retrieval | No. The manual explicitly says compatibility with all USB-A ports is not guaranteed. |
| TC16 | What should I do if the headset turns off automatically? | Troubleshooting | Check the inactivity timeout and battery charge; the manual describes automatic shutdown under specified conditions. |
| TC17 | How do I mute the microphone? | Control instructions | Press the microphone mute/unmute button on the headset. |
| TC18 | What is the impedance, and what is the microphone sensitivity? | Two-specification retrieval | 32 ohms and −42 dBV/Pa at 1 kHz. |
| TC19 | How do I charge the headset, and how do I pair it afterward? | Multi-step synthesis | Explains charging via USB-A to USB-C, then connecting the dongle and powering on, with manual pairing if needed. |
| TC20 | What is the headset's Bluetooth pairing procedure? | Unsupported premise | Should clarify that this manual describes a 2.4G USB wireless dongle connection, not provide an invented Bluetooth procedure. |

    Reference: the manual's charging, connection, specification, and troubleshooting sections.


## 3. Conversational memory test

Run these questions in the same chat session, in order. Don't start a new conversation between them.

### TC21 — Context retention

Question 1: How long does the JBL Quantum 350 take to charge?

Expected: Approximately 2 hours.

Question 2: And how long does it last on a full charge?

Expected: Up to 22 hours of music playback.

Pass condition: The bot understands that “it” refers to the JBL headset and retrieves the second fact correctly.

### TC22 — Follow-up troubleshooting

Question 1: How do I pair the headset manually?

Expected: Hold the dongle's pairing button for more than 5 seconds, until the LED flashes quickly.

Question 2: What should I see when it succeeds?

Expected: Both the headset and dongle LEDs turn solid white.

Pass condition: The bot resolves the follow-up without asking which device or pairing process you mean.

## 4. Unanswerable questions and hallucination tests

These tests are just as important as factual questions. Your prompt tells the LLM to answer only from retrieved context, so it should acknowledge when the manual doesn't contain the requested information.

| ID | Question | Expected behavior |
| --- | --- | --- |
| TC23 | What is the current retail price of the headset? | Say the manual doesn't provide the current price. |
| TC24 | Does this headset support Bluetooth 5.3? | Say the manual does not establish that specification; don't invent a version. |
| TC25 | What is the warranty duration in India? | Say the manual's listed contents include a warranty card, but the supplied manual does not specify the duration. |
| TC26 | What is the serial number of my headset? | Explain that the manual cannot provide a serial number for the user's individual device. |
| TC27 | Does the headset have active noise cancellation? | Don't assert that it does unless supporting documentation is available. |
| TC28 | What is the headset's battery capacity? | Answer 500 mAh, with the source citation. This is a positive control alongside the unanswerable tests. |

These are deliberately chosen to distinguish retrieval-grounded answers from plausible-sounding guesses.




