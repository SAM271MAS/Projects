#include <iostream>
#include <fstream>
#include <regex>
#include <chrono>
#include <string>
#include <algorithm>
#include <vector>
#include <unordered_map>
#include <ios>
#include "HashMap.h"
#include "FileUtils.h"

#include <thread>
#include <mutex>
#include <atomic>

using namespace std;

int main(int argc, char **argv)
{
        using namespace std::chrono;

        // Allow filename as optional first argument, default to project-root/WarAndPeace.txt
        // Optional second argument is mode (e.g. "freqstd" or "freq").
        // Optional third argument is num_threads (default 4).
        string filename = "../WarAndPeace.txt";
        string mode = "freqstd";
        int num_threads=4;
        if (argc > 1)
                filename = argv[1];
        if (argc > 2)
                mode = argv[2];

        if (argc > 3) 
            num_threads = std::stoi(argv[3]);

        // Check if file is readable
        ifstream check(filename, std::ios::binary);
        if (!check.is_open())
        {
                cerr << "Could not open '" << filename << "'. Please provide a readable text file as the first argument." << endl;
                cerr << "Usage: " << (argc > 0 ? argv[0] : "TME3") << " [path/to/textfile] [mode] [num threads]" << endl;
                return 2;
        }
        check.seekg(0, std::ios::end);
        std::streamoff file_size = check.tellg();
        check.close();

        cout << "Preparing to parse " << filename << " (mode=" << mode << " N=" << num_threads << "), containing " << file_size << " bytes" << endl;

        auto start = steady_clock::now();

        std::vector<std::pair<std::string, int>> pairs;

        if (mode == "freqstd") {
                ifstream input(filename, std::ios::binary);
                size_t total_words = 0;
                size_t unique_words = 0;
                std::unordered_map<std::string, int> um;
                std::string word;
                while (input >> word) {
                        word = pr::cleanWord(word);
                        if (!word.empty()) {
                                total_words++;
                                ++um[word];
                        }
                }
                unique_words = um.size();
                pairs.reserve(unique_words);
                for (const auto& p : um) pairs.emplace_back(p);
                pr::printResults(total_words, unique_words, pairs, mode + ".freq");

        } else if (mode == "freqstdf") {
                size_t total_words = 0;
                size_t unique_words = 0;
                std::unordered_map<std::string, int> um;
                pr::processRange(filename, 0, file_size, [&](const std::string& word) {
                        total_words++;
                        um[word]++;
                });
                unique_words = um.size();
                pairs.reserve(unique_words);
                for (const auto& p : um) pairs.emplace_back(p);
                pr::printResults(total_words, unique_words, pairs, mode + ".freq");

        } else if (mode == "freq") {
                size_t total_words = 0;
                size_t unique_words = 0;
                HashMap<std::string, int> hm;
                pr::processRange(filename, 0, file_size, [&](const std::string& word) {
                        total_words++;
                        hm.incrementFrequency(word);
                });
                pairs = hm.toKeyValuePairs();
                unique_words = pairs.size();
                pr::printResults(total_words, unique_words, pairs, mode + ".freq");

        } else if (mode == "partition") {
            size_t total_count = 0;
            std::unordered_map<std::string, int> counts;
            auto chunks = pr::partition(filename, file_size, num_threads); // Décopue en N

            for (size_t i = 0; i < chunks.size() - 1; ++i) {
                    pr::processRange(filename, chunks[i], chunks[i+1], [&](const std::string& token) {
                        total_count++;
                        counts[token]++;
                    });
                }
                
                pairs.reserve(counts.size());
                for (const auto& kv : counts) pairs.emplace_back(kv);
                pr::printResults(total_count, counts.size(), pairs, mode + ".freq");

        } else if (mode == "mt_naive") {
            size_t total_count = 0;
                std::unordered_map<std::string, int> counts;
                
                auto chunks = pr::partition(filename, file_size, num_threads);
                std::vector<std::thread> workers;

                // data race 
                for (int i = 0; i < num_threads; ++i) {
                    workers.emplace_back([&, i]() {
                        pr::processRange(filename, chunks[i], chunks[i+1], [&](const std::string& token) {
                            total_count++;  // ici
                            counts[token]++; // ici
                        });
                    });
                }

                for (auto& w : workers) w.join();

                pairs.reserve(counts.size());
                for (const auto& kv : counts) pairs.emplace_back(kv);
                pr::printResults(total_count, counts.size(), pairs, mode + ".freq");

        } else if (mode == "mt_mutex") {
            size_t total_count = 0;
                std::unordered_map<std::string, int> counts;
                std::mutex safe_lock; // Le verrou

                auto chunks = pr::partition(filename, file_size, num_threads);
                std::vector<std::thread> workers;

                for (int i = 0; i < num_threads; ++i) {
                    workers.emplace_back([&, i]() {
                        pr::processRange(filename, chunks[i], chunks[i+1], [&](const std::string& token) {
                            // On verrouille avant d'écrire
                            std::lock_guard<std::mutex> guard(safe_lock);
                            total_count++;
                            counts[token]++;
                        });
                    });
                }

                for (auto& w : workers) w.join();

                pairs.reserve(counts.size());
                for (const auto& kv : counts) pairs.emplace_back(kv);
                pr::printResults(total_count, counts.size(), pairs, mode + ".freq");

        } else if (mode == "mt_hashes") {
                std::atomic<size_t> atomic_total{0};
                // Chaque thread possède sa propre map pour éviter les conflits
                std::vector<std::unordered_map<std::string, int>> local_maps(num_threads);
                
                auto chunks = pr::partition(filename, file_size, num_threads);
                std::vector<std::thread> workers;

                for (int i = 0; i < num_threads; ++i) {
                    workers.emplace_back([&, i]() {
                        // On écrit dans local_maps[i] uniquement
                        pr::processRange(filename, chunks[i], chunks[i+1], [&](const std::string& token) {
                            atomic_total++; 
                            local_maps[i][token]++;
                        });
                    });
                }

                for (auto& w : workers) w.join();

                std::unordered_map<std::string, int> final_map;

                for (const auto& thread_map : local_maps) {
                    for (const auto& entry : thread_map) {
                        final_map[entry.first] += entry.second;
                    }
                }

                pairs.reserve(final_map.size());
                for (const auto& kv : final_map) pairs.emplace_back(kv);
                pr::printResults(atomic_total, final_map.size(), pairs, mode + ".freq");


        } else {
                cerr << "Unknown mode '" << mode << "'. Supported modes: freqstd, freq, freqstdf" << endl;
                return 1;
        }

        // print a single total runtime for successful runs
        auto end = steady_clock::now();
        cout << "Total runtime (wall clock) : " << duration_cast<milliseconds>(end - start).count() << " ms" << endl;

        return 0;
}

