import os
import dotenv
from openai import OpenAI
from source.retriever.mapping_elastic import RetrieveHelper
from configs.config_system import LoadConfig

dotenv.load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


tools = [
        {
            "type": "function",
            "function": {
                "name": "get_specifications",
                "description": """Lấy ra loại hoặc tên sản phẩm và các thông số kỹ thuật của sản phẩm có trong câu hỏi. Sử dụng khi câu hỏi có thông tin về 1 trong các các thông số [loại hoặc tên sản phẩm,  giá, cân nặng, công suất hoặc dung tích]""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "group": {
                            "type": "string",
                            "description": f"""lấy ra nhóm sản phẩm có trong câu hỏi từ list: {LoadConfig.LIST_GROUP_NAME}. 
                            Chỉ trả ra tên group có trong list đã cho trước
                            Một số ngoại lệ khi phân group:
                                - cáp chạy phần mềm,cáp faceid, thanh fix pin, thiết bị test sóng, cáp loa sàng, thanh fix pin, thanh fix màn, thiết bị đo dòng sạc và điện áp, thiết bị kiểm tra, thiết bị tự động phát hiện lỗi chân sạc thì 'group': 'box, đế test, cáp'
                                - Ron nồi hấp, miếng lót màn hình chịu nhiệt thì 'group': 'cao su'
                                - máy hút khói bụi, máy thổi, dụng cụ lấy bụi, nước tách, nồi luộc main thì 'group': 'dung dịch, vệ sinh'
                                - Miếng đồng ép điểm sửa chữa thì 'group': 'dây đồng, dây cắt'
                                - hộp đựng tô vit, miếng gạt dán điện thoại, khay gỗ, kéo gốm cắt cell,chữ T cắt film, quạt sửa chữa làm mát main, sủi nhựa thì 'group': 'dụng cụ'
                                - dụng cụ hỗ trợ bơm keo tuýp, dung dịch tạo phấn camera, đệm nhiệt, miếng dính lột màng keo OCA, miếng tản nhiệt đồng, bộ đầu nối dùng cho các lọ keo, đầu bơm keo kim loại, miếng dán bảo vệ camera, súng bắn keo thì 'group': 'keo dán, keo uv, băng dính'
                                - đế nam châm, đế kẹp main Iphone, bộ làm chân, khuôn Iphone, đế nam châm WL, vỉ làm chân viền MAANT, đế kẹp main, khuôn vỉ iPhone thì 'group': 'khuôn, đế làm chân ic'
                                - Quạt hút khói thiếc gắn kính hiển vi, Ống kính phóng to kính hiển vi, Ống nâng chiều cao kính hiển vi, Camera kính hiển vi, đèn kính hiển vi thì 'group': 'phụ kiện kính hiển vi'
                                - dụng cụ kẹp, đế kẹp camera, dụng cụ kẹp FaceID, đế kính hiển vi, đế Kẹp FaceID, đế hít màn hình hỗ trợ tháo máy thì 'group': 'kẹp main, điện thoại, face'
                                - Bộ 5 đầu kẹp mũi khoan, mũi mài kèm khớp nối ĐỒNG, Lưỡi cắt tròn mỏng, đế giữ cố định máy mài, dụng cụ kẹp lưỡi cắt, Đá mài panh nhíp, mũi hàn, lưỡi dao thì  'group': 'máy mài, cắt & pk'
                                - Đầu bông đánh bóng, lấy keo, dụng cụ tuốt keo 1 khe thì 'group': 'máy cuốn keo & pk'
                                - thiết bị đo dòng sạc, kích pin, cáp tháo pin nhanh, Ổ cắm điện tích hợp 3 cổng USB, Kích pin, bộ dây đầu kẹp cá sấu, cáp tháo pin nhanh thì 'group': 'máy cấp nguồn & pk'
                                - Máy cắt kính nguyên cây thì 'group': 'máy ép kính & pk'
                                - 10 bộ cao su dán Socket main iPhone, Màng loa iPhone thì 'group': 'siu, nẹp, ốc'
                                - Sạc báo dòng thì 'group': 'sạc nhiều cổng'                                                                                                                                                                                   
                                - Bộ dụng cụ lấy mắt camera , Khay xốp để điện thoại, màn hình, Miếng nhựa đa năng hỗ trợ tháo điện thoại, miếng kim loại mỏng tạo khe tách màn, Bút phá kính, dụng cụ hỗ trợ tháo viền camera, Bộ dụng cụ hỗ trợ đục lưng, Bộ dụng cụ lấy mắt camera, Miếng tách nạy màn hình điện thoại đa năng, miếng tách thì 'group': 'tool tháo máy'
                            """
                        },
                        "object": {
                            "type": "string",
                            "description": f"""tên hoặc loại sản phẩm có trong câu hỏi. Ví dụ: kính, tô vít ...
                            Một số ngoại lệ khi lấy object:
                                - vỏ điện thoại samsung thì 'object':'vỏ samsung'
                                - tôi hỏi máy hàn cơ thì 'object':'máy hàn'
                                - hộp đựng tô vít thì 'object':'hộp để tô vít')
                                - viền ron iphone thì 'object':'viền ron iphone'
                                - Cáp nối dài gắn chân pin thì 'object':'cáp nối dài gắn chân pin'
                                - Vòng ron cao su camera iPhone thì 'object':'vòng ron cao su camera iPhone'
                                - Dao lam dầy đại bàng Flying Eagle H3000 thì 'object': 'Dao lam dầy đại bàng Flying Eagle H3000'
                                - Hộp 6 mũi mài thì 'object': 'hộp 6 mũi mài' 
                                - Đầu bông đánh bóng, lấy keo thì 'object': 'đầu bông đánh bóng, lấy keo'
                                - Máy cắt kính nguyên cây thì 'object': 'máy cắt kính nguyên cây'
                                - Vỉ Huawei Maant - P50Pro thì 'object': 'vỉ Huawei Maant - P50Pro'(vỉ làm chân thì lấy object thao tên người dùng gửi)
                            """
                        },
                        "price": {
                            "type": "string",
                            "description": "giá của sản phẩm có trong câu hỏi. Ví dụ : 1 triệu, 1000đ, ...",
                        },
                        "intent": {
                            "type": "string",
                            "description": "ý định của người dùng khi hỏi câu hỏi. Ví dụ: mua, tìm hiểu, so sánh, ..."
                        }
                    },
                    "required": ["group", "object", "price", "intent"],
                },
            },
        }
    ]

def extract_info(query: str):
    client = OpenAI(timeout=LoadConfig.TIMEOUT)

    messages = [
        {'role': 'system', 'content': '''Bạn là 1 chuyên gia extract thông tin từ câu hỏi. 
        Hãy giúp tôi lấy các thông số kỹ thuật, tên hoặc loại của sản phẩm có trong câu hỏi
        Lưu ý:
            + nếu câu hỏi hỏi về các thông số lớn, nhỏ, rẻ, đắt... thì trả ra cụm đó. 
            + Nếu không có thông số nào thì trả ra '' cho thông số ấy.
            + 1 số tên sản phẩm có chứa cả thông số thì bạn cần tách thông số đó sang trường của thông số đó'''},
        {"role": "user", "content": query}]

    openai_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="auto",  # auto is default, but we'll be explicit
        )
    
     # if openai_response.choices[0].message.tool_calls:
    #     for i in range(0, len(openai_response.choices[0].message.tool_calls)):
    #         print(f"Function: {openai_response.choices[0].message.tool_calls[i].function.name}\n")
    #         print(f"Arguments: {openai_response.choices[0].message.tool_calls[i].function.arguments}\n")
    arguments = openai_response.choices[0].message.tool_calls[0].function.arguments
    
    specifications = RetrieveHelper().parse_string_to_dict(arguments)
    return specifications


def main():
    arguments = extract_info("Tôi muốn mua điều hòa rẻ nhất")
    json_arguments = RetrieveHelper().parse_string_to_dict(arguments)
    print(json_arguments)
    for key, value in json_arguments.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()