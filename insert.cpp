#include <iostream>
#include <string>
extern "C" {
    #include "sqlite3.h"
}

int main(int argc, char* argv[]) {
    std::cout << "argc = " << argc << "\n";
    for (int i = 0; i < argc; ++i) {
        std::cout << "argv[" << i << "] = " << argv[i] << "\n";
    }

    if (argc != 6) {
        std::cerr << "❌ Usage: insert <roll> <name> <course> <phone> <address>\n";
        return 1;
    }

    // Parse roll number safely
    int roll;
    try {
        roll = std::stoi(argv[1]);
    } catch (...) {
        std::cerr << "❌ Invalid roll number\n";
        return 1;
    }

    const char* name = argv[2];
    const char* course = argv[3];
    const char* phone = argv[4];
    const char* address = argv[5];

    sqlite3* db;
    sqlite3_stmt* stmt;

    // Open database
    if (sqlite3_open("students.db", &db)) {
        std::cerr << "❌ Cannot open database: " << sqlite3_errmsg(db) << "\n";
        return 1;
    }

    // Ensure table exists
    const char* create_sql =
        "CREATE TABLE IF NOT EXISTS students ("
        "roll INTEGER PRIMARY KEY, "
        "name TEXT NOT NULL, "
        "course TEXT NOT NULL, "
        "phone TEXT, "
        "address TEXT);";

    char* errMsg = nullptr;
    if (sqlite3_exec(db, create_sql, nullptr, nullptr, &errMsg) != SQLITE_OK) {
        std::cerr << "❌ Table creation error: " << errMsg << "\n";
        sqlite3_free(errMsg);
        sqlite3_close(db);
        return 1;
    }

    // Prepare insert statement
    const char* insert_sql = "INSERT INTO students (roll, name, course, phone, address) VALUES (?, ?, ?, ?, ?);";

    if (sqlite3_prepare_v2(db, insert_sql, -1, &stmt, nullptr) != SQLITE_OK) {
        std::cerr << "❌ Prepare failed: " << sqlite3_errmsg(db) << "\n";
        sqlite3_close(db);
        return 1;
    }

    // Bind values
    sqlite3_bind_int(stmt, 1, roll);
    sqlite3_bind_text(stmt, 2, name, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 3, course, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 4, phone, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 5, address, -1, SQLITE_STATIC);

    // Execute insert
    int rc = sqlite3_step(stmt);
    if (rc == SQLITE_DONE) {
        std::cout << "✅ Student added successfully.\n";
    } else {
        std::cerr << "❌ Insert failed: " << sqlite3_errmsg(db) << "\n";
    }

    // Cleanup
    sqlite3_finalize(stmt);
    sqlite3_close(db);
    return 0;
}
