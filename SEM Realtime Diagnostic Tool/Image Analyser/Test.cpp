/*	File:			Test.cpp

	Description:	Testbench for code.

	Author:			Liuchuyao Xu
*/

#include <iostream>
#include <fstream>

using namespace std;

int main()
{
	ifstream image;
	auto image_path = "../../SEM Images/Armin241.tif";

	image.open(image_path, ios::binary);
	
	char c {};
	int  i {};
	while(i < 200) {
		image.get(c);
		cout << static_cast<int>(c) << " ";
		i++;
	}

	return 0;
}
