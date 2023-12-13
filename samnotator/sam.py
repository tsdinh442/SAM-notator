from segment_anything import SamAutomaticMaskGenerator, sam_model_registry
import torch


device = 'mps' if torch.backends.mps.is_available() else 'cpu'

check_point = 'models/sam_vit_h_4b8939.pth'

sam = sam_model_registry["default"](checkpoint=check_point)
sam.to(device=device)

mask_generator = SamAutomaticMaskGenerator(model=sam,
                                           points_per_side=32,
                                           pred_iou_thresh=0.9,
                                           stability_score_thresh=0.96)

