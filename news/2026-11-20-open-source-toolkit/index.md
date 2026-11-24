---
title: "Our toolkit is open source"
description: "The software we use to find birds, bats and moths in recordings and photos is now free for anyone to use, in Python or R."
date: 2026-11-20
author: "UKCEH Tech for Nature"
categories: [News, Software]
---

The tools we use to turn photos and sound recordings into wildlife records are now open source, on [GitHub](https://github.com/NERC-CEH/ceh-biomonitoring). They run on a laptop, on JASMIN or on another computing cluster, and you can drive them from Python or from R.

**What it does:**

- **Birds** in sound recordings, with BirdNET or Perch.
- **Bats** in ultrasonic recordings, with BatDetect2.
- **Moths and other insects** in light-trap photos from AMI traps and LepiSense: it finds each insect, tells moths from other insects, names the moth species with a model for your region, and follows each insect from photo to photo.
- **Expert checking.** The models make mistakes, so the toolkit picks a fair sample for experts to check: audio clips with spectrograms, or photos in [Mothbot](https://mothbot-classify.vercel.app).
- **Reports.** Tables of nights (with the weather and the moon), individuals and species that work with [EntoInsights](https://github.com/AMI-system/EntoInsights), and summary reports in HTML, Word and PDF.

New to it? Start with our [Do it yourself](../../how-to/do-it-yourself.qmd) guide, which points to the right place for each step.
