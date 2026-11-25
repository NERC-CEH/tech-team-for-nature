---
title: "How the AI works: machine learning at the edge"
description: "From a white screen covered in insects to species names: how AMI systems find, sort and recognise wildlife."
date: 2025-09-05
author: "AMBER team"
image: cover.jpg
categories: [Story, AMBER, AI, AMI light traps]
---

<!-- the six clips were 37 MB GIFs on the old site; they're now short looping videos -->

## Automated Monitoring of Insects (AMI)

AMI systems are smart camera traps built for remote and off-grid biodiversity monitoring. Designed by ecologists and engineers, they capture images in the field and run machine learning models directly on the device, with no internet needed.

<video class="loop" src="ami-system.mp4" poster="ami-system.jpg" autoplay loop muted playsinline aria-label="An AMI system with insects landing on its screen"></video>

## Why machine learning at the edge?

Each AMI system can capture thousands of images a week, often in places with no power or connectivity. Machine learning at the edge processes data locally: filtering out noise, flagging wildlife, and keeping only the most relevant images.

<video class="loop" src="raw-images.mp4" poster="raw-images.jpg" autoplay loop muted playsinline aria-label="The white screen with insects landing on it"></video>

## Finding wildlife in the pictures

Our models first find the animals in each image (object detection). This step filters out empty frames and crops out each animal, ready for the next steps, all on a low-power device.

<video class="loop" src="flatbug-images.mp4" poster="flatbug-images.jpg" autoplay loop muted playsinline aria-label="Each insect on the screen outlined by a grey box"></video>

## Sorting life into orders

Once found, each animal is sorted into a broad group, such as spiders, flies or moths (Lepidoptera). This coarse sorting helps prioritise images and balances accuracy against computing power.

<video class="loop" src="order-images.mp4" poster="order-images.jpg" autoplay loop muted playsinline aria-label="Moths outlined in green and other insects in red"></video>

## Recognising species in seconds

Compact neural networks then name the species from each crop. The models are small enough to run on solar-powered hardware, yet accurate enough to tell similar-looking species apart.

<video class="loop" src="species-images.mp4" poster="species-images.jpg" autoplay loop muted playsinline aria-label="Moths outlined in green with their species names, other insects in red"></video>

## Tracking individuals

We're exploring ways to follow the same individual across frames, or even between camera sites. This helps us study behaviour and movement, and avoid counting the same moth twice.

<video class="loop" src="tracking-images.mp4" poster="tracking-images.jpg" autoplay loop muted playsinline aria-label="Each insect outlined in its own colour, followed from frame to frame"></video>

---

**Next:** [where AMBER works](../../map/index.qmd) · [wildlife encounters](../2025-09-05-amber-wildlife-encounters/index.md) · [run the models yourself](https://github.com/NERC-CEH/ceh-biomonitoring)
