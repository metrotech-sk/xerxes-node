//serialization stuf
#include <Packet.h>
#include <PacketCrc.h>
#include <VectorSerialization.h>
#include <VectorDeserialization.h>
#include <PacketSerializer.h>
#include <VectorCrc.h>

//protocol stuff
#include <MsgReader.h>
#include <AsyncMsgReader.h>
#include <RequestResponseClient.h>
#include <Packet.hpp>

#include <rs485.h>
#include <signal.h>
#include <atomic>

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
    std::vector<RequestResponseClient<MsgReader, uint8_t, std::array<uint8_t, 2>>> clients; //= {
//            std::move(RequestResponseClient<MsgReader, uint8_t, uint8_t> (0, 6, bus, asyncMsgReader))};
    clients.emplace_back(RequestResponseClient<MsgReader, uint8_t, std::array<uint8_t, 2>> (0, 6, bus, asyncMsgReader));
    UpdateExecutor executor(asyncMsgReader);
    while (!terminate)
    {
        const auto start = std::chrono::high_resolution_clock::now();
        for(auto& client : clients)
        {
            auto res = client.call(34);
            auto msg = res->wait(std::chrono::milliseconds(1000));
            std::cout << "From: " << std::hex << int(msg.header.srcAdr) << " Data: " << msg.data << std::endl;
        }
        std::this_thread::sleep_for(std::chrono::seconds(1) - (std::chrono::high_resolution_clock::now() - start));
    }

    return 0;
}
