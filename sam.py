from segment_anything import SamAutomaticMaskGenerator, sam_model_registry
import torch
#import cv2

#image_path = 'src/images/1.jpeg'
#image = cv2.imread(image_path)
#image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

device = 'mps' if torch.backends.mps.is_available() else 'cpu'

check_point = 'models/sam_vit_h_4b8939.pth'

sam = sam_model_registry["default"](checkpoint=check_point)
sam.to(device=device)

mask_generator = SamAutomaticMaskGenerator(sam)
#masks = mask_generator.generate(image)

