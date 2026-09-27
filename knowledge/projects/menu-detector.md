# Project: Menu Detector — Food Image Classifier

## Summary
Menu Detector is a deep learning model that looks at a food photo and classifies it into one of five classes: hamburger, hot dog, dessert, kebab or pizza. Juno fine-tuned an ImageNet-pretrained MobileNetV2 with PyTorch on Google Colab.
Code: https://github.com/khodiboev/computer_vision

## Results
- Validation accuracy: 93.7%
- Balanced accuracy (average recall per class): 94.8%
- Kebab recall: 100% (kebab was the smallest class)
- Dataset: 4,113 images, stratified 80/20 train/validation split
- Training time: about 3 minutes on a T4 GPU

## The data problem
Food-101 has no kebab class, so kebab images were scraped from Bing. About 90% of the scraped images turned out to be unrelated noise such as ads, logos and photos of people. Juno cleaned them in three layers: removing broken, tiny and duplicate images with perceptual hashing, then CLIP zero-shot filtering to score each image as "kebab" versus noise, then a short manual review. 478 raw images became 24 approved ones.

## Handling class imbalance
Even after cleaning, kebab had about nine times fewer images than other classes. Juno used a class-weighted loss, a stratified split, data augmentation and capped the merged dessert class, and he selected the best model by balanced accuracy instead of plain accuracy.

## Improving the course version
The project began as a course exercise with 89% accuracy. Juno found seven problems in it — including an empty class, validation code outside the training loop and no augmentation — and rebuilt the notebook. Per-epoch validation showed overfitting after epoch 5, so the epoch-5 checkpoint was kept.

## Tech stack
Python, PyTorch, torchvision, scikit-learn, Hugging Face Transformers (CLIP), imagehash, pandas, Matplotlib, Google Colab.
