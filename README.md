# 🎬 DriftWatch Video

**Why do AI-generated videos drift, flicker and lose identity over time — and how do we fix it?**
**ทำไมวิดีโอที่สร้างด้วย AI ถึงเพี้ยน กระพริบ และเสียความต่อเนื่องของตัวละคร และจะแก้อย่างไร?**

An open research project by PureFxAi studying **temporal consistency** in AI video: an open benchmark and metrics for *drift* (faces, objects, colours and physics changing across frames) in open-weight video generation models, plus tests of lightweight methods to reduce it.

โครงการวิจัยเปิดโดย PureFxAi ศึกษา **ความต่อเนื่องตามเวลา** ของวิดีโอ AI: สร้างชุดทดสอบและตัวชี้วัดแบบเปิดสำหรับการ "เพี้ยน" (ใบหน้า วัตถุ สี ฟิสิกส์ที่เปลี่ยนระหว่างเฟรม) ในโมเดลสร้างวิดีโอแบบ open-weight แล้วทดลองวิธีลดปัญหานี้

> **Status: early stage.** No results exist yet. Everything published will include code, prompts, seeds and raw videos to reproduce it.
> **สถานะ: ระยะเริ่มต้น** ยังไม่มีผลลัพธ์ ทุกผลที่เผยแพร่จะมีโค้ด prompt seed และวิดีโอดิบให้ทำซ้ำได้

## ❓ Research questions / คำถามวิจัย
1. Can drift be measured automatically in a way that agrees with human judgement? / วัดการเพี้ยนอัตโนมัติให้ตรงกับการตัดสินของคนได้หรือไม่
2. How does drift grow with clip length, motion and number of subjects? / การเพี้ยนเพิ่มขึ้นอย่างไรตามความยาว การเคลื่อนไหว และจำนวนตัวละคร
3. Which training-free methods (reference frames, feature caching, guidance tweaks) reduce drift, at what compute cost? / วิธีที่ไม่ต้องเทรนใหม่แบบไหนลดการเพี้ยนได้ และใช้ทรัพยากรเท่าไร
4. Can video-understanding models flag drifted segments for regeneration? / โมเดลเข้าใจวิดีโอตรวจจับช่วงที่เพี้ยนเพื่อสร้างใหม่ได้หรือไม่

## 🗺️ Roadmap
- [ ] **Phase 1** — Open prompt suite (people, animals, objects, camera motion) + human rating protocol
- [ ] **Phase 2** — Drift metrics (identity-embedding similarity, colour/optical-flow stability) validated against human ratings
- [ ] **Phase 3** — Benchmark open-weight video models; publish raw outputs
- [ ] **Phase 4** — Test & report mitigation methods, including negative results

## 🤝 Contributing / ร่วมพัฒนา
Help with prompts, human ratings, metrics or GPU time is welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) and [research/TEMPLATE.md](research/TEMPLATE.md).

## 💚 Donate USDT / สนับสนุนด้วย USDT
Donations fund compute (GPU hours) and dataset review. / เงินบริจาคใช้ค่าประมวลผลและการตรวจสอบชุดข้อมูล

**Network: Ethereum (ERC20) only / เครือข่าย Ethereum (ERC20) เท่านั้น**

```
0x920deab53daf94ca2030ad5ceec2265bf5686941
```

<img src="docs/usdt-erc20-qr.png" width="200" alt="USDT ERC20 QR">

Donation page: https://purefxaidev.github.io/khwamjing-bench/

⚠️ Send **only USDT via ERC20**. Other networks or tokens may be lost permanently.
ส่งเฉพาะ **USDT ผ่าน ERC20** เท่านั้น เครือข่ายหรือเหรียญอื่นอาจสูญหายถาวร

Donations are voluntary support — **not an investment**, with no returns or rewards.
การบริจาคเป็นการสนับสนุนโดยสมัครใจ **ไม่ใช่การลงทุน** และไม่มีผลตอบแทนใด ๆ

## License
Code: MIT. Prompt suite & ratings (when released): CC-BY-4.0.
