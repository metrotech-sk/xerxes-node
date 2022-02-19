#include <Packet.h>
#include <Serialization.h>
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

int main(int argc, char** argv){
    signal(SIGINT,sig_handler);
    signal(SIGTERM,sig_handler);
    std::shared_ptr<ABus> bus = std::make_shared<Xerxes::RS485>("");
    AsyncMsgReader<MsgReader> asyncMsgReader(MsgReader(bus, std::chrono::milliseconds(10)),{});
    RequestResponseClient<MsgReader, uint8_t, uint8_t> (1, 2, bus, asyncMsgReader);
    std::vector<RequestResponseClient<MsgReader, uint8_t, uint8_t>> clients = {
            RequestResponseClient<MsgReader, uint8_t, uint8_t> (1, 2, bus, asyncMsgReader)};
    UpdateExecutor executor(asyncMsgReader);
//    while (!terminate)
    {
        const auto start = std::chrono::high_resolution_clock::now();
        std::cout << std::endl << std::endl;

        for(auto& client : clients)
        {
            auto res = client.call(5);
            res.wait();
            std::cout << res.get() << std::endl;
        }
        std::this_thread::sleep_for(std::chrono::seconds(1) - (std::chrono::high_resolution_clock::now() - start));
    }
    return 0;
}
