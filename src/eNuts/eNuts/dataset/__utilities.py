# ==================================================================================
from torch.utils.data import default_collate


# ==================================================================================
def va_collate(batch):
    # Filter out None entries returned from skipped duplicate windows
    batch = [item for item in batch if item is not None]
    if not batch:
        return None
    return default_collate(batch)
