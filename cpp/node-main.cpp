#include <Packet.h>
#include <Serialization.h>
#include <VectorSerialization.h>
#include <Deserialization.h>
#include <VectorDeserialization.h>
#include <PacketSerializer.h>
#include <MsgReader.h>
#include <AsyncMsgReader.h>
#include <rs485.h>
#include <RequestResponseClient.h>
#include <chrono>
#include <signal.h>

std::atomic<bool> terminate = false;
void sig_handler(int signum){
    terminate = true;
}

template<typename T, size_t size>
std::ostream& operator<<(std::ostream& stream, const std::array<T, size>& data) {
    for(const auto& i : data){
        stream << std::hex << int(i) << ", ";
    }
    return stream;
}

int main(int argc, char** argv){
    signal(SIGINT,sig_handler);
    signal(SIGTERM,sig_handler);
    std::shared_ptr<ABus> bus = std::make_shared<Xerxes::RS485>("/dev/ttyUSB0");
    AsyncMsgReader<MsgReader> asyncMsgReader(MsgReader(bus, std::chrono::milliseconds(10)),{});
    //todo initializer list
    std::vector<RequestResponseClient<MsgReader, uint8_t, Packet<std::array<uint8_t, 2>>>> clients; //= {
//            std::move(RequestResponseClient<MsgReader, uint8_t, uint8_t> (0, 6, bus, asyncMsgReader))};
    clients.emplace_back(RequestResponseClient<MsgReader, uint8_t, Packet<std::array<uint8_t, 2>>> (0, 6, bus, asyncMsgReader));
    UpdateExecutor executor(asyncMsgReader);
    while (!terminate)
    {
        const auto start = std::chrono::high_resolution_clock::now();
        for(auto& client : clients)
        {
            auto res = client.call(2);
            std::cout << "Received: " << std::hex << res->wait(std::chrono::milliseconds(1000)).data << std::endl;
        }
        std::this_thread::sleep_for(std::chrono::seconds(1) - (std::chrono::high_resolution_clock::now() - start));
    }

    return 0;
}
