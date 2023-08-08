#include "duckdb.hpp"
#include <iostream>
#include "utils/ConfigFactory.h"

using namespace duckdb;

int main() {
	DuckDB db(nullptr);
	Connection con(db);
	std::string demo = ConfigFactory::Instance().getPixelsDirectory() + "cpp/tests/data/example.pxl";
	auto result = con.Query("SELECT * from '" + demo + "';");
	result->Print();
}
