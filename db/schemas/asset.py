"""Asset schema"""

def asset_schema(asset) -> dict:
    return {"id": str(asset["_id"]),
            "user_id": asset["user_id"],
            "mnemonic": asset["mnemonic"],
            "price": asset["price"],
            "shares": asset["shares"]}


def assets_schema(assets) -> list:
    return [asset_schema(asset) for asset in assets]
