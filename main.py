from selenium import webdriver
from selenium.webdriver.common.keys import Keys
# from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support.ui import Select
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import time
import random
import h5py
import pickle,sys,traceback,os

if __name__ == "__main__":
	try:
		frec = open('records.txt','a')
		facc = open('accuracy.txt','a')
		firefoxProfile = FirefoxProfile()
		firefoxProfile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so','false')
		f = h5py.File('main.hdf5','r+')
		driver = webdriver.Firefox(firefoxProfile)
		driver.get("http://www.saltybet.com/authenticate?signin=1")
		try:
			cookies = pickle.load(open("cookies.pkl", "rb"))
			for cookie in cookies:
				driver.add_cookie(cookie)
		except Exception, e:
			print "Error with cookie"
		driver.get("http://saltybet.com/mobile")
		if "Sign in" in driver.find_element_by_xpath("//span[@id='betstatus']").text:
			wait = WebDriverWait(driver, 100)
			driver.get("http://www.saltybet.com/authenticate?signin=1")
			time.sleep(1)

			inputElement = driver.find_element_by_xpath("//input[@id='email']")
			inputElement.send_keys("email")

			inputElement = driver.find_element_by_xpath("//input[@id='pword']")
			inputElement.send_keys("password")
			inputElement.send_keys(Keys.RETURN);
			# inputElement = driver.find_element_by_xpath("//input[@type='submit']")
			# inputElement.click()

			driver.get("http://saltybet.com/mobile")
		time.sleep(5)
		betstatusid = 0
		lastbet = 'blue'
		alreadybet = False
		lastwon = 'blue'
		correct = [0,0,0]
		total = [0,0,0]
		unknown = 0
		monies = int(driver.find_element_by_xpath("//span[@id='balance']").get_attribute("innerHTML"))
		while(True):
			betstatus = driver.find_element_by_xpath("//span[@id='betstatus']").get_attribute("innerHTML")
			if "Bets are locked" in betstatus and betstatusid != 1:
				print "Bets closed"
				print "--------------------------------------------------------"
				betstatusid = 1
				time.sleep(2)
				potential = driver.find_element_by_xpath("//span[@id='odds']").text
				if '$' in potential and alreadybet == False:
					alreadybet = True
					betodds = driver.find_element_by_xpath("//span[@id='lastbet']").get_attribute("innerHTML")
					if 'redtext' in betodds:
						lastbet = 'red'
					else:
						lastbet = 'blue'
					redPlayer = driver.find_element_by_xpath("//span[@id='p1name']").get_attribute("innerHTML")
					bluePlayer = driver.find_element_by_xpath("//span[@id='p2name']").get_attribute("innerHTML")
					if f.get(redPlayer) is None:
						f[redPlayer] = 1400
					if f.get(bluePlayer) is None:
						f[bluePlayer] = 1400
					Rb = float(f[bluePlayer].value)
					Rr = float(f[redPlayer].value)
					Er = 1.0/(1+10**((Rb-Rr)/400))
					Eb = 1.0/(1+10**((Rr-Rb)/400))
					print 'Resuming from previous session:'
					print redPlayer+'['+str(Rr)+']', 'vs', bluePlayer+'['+str(Rb)+']'
				if alreadybet:
					potential = driver.find_element_by_xpath("//span[@id='odds']").text
					print "Odds:", potential
					if potential == "N/A":
						alreadybet = False
				print "Current monies: $" + str(monies)
			elif "Bets are OPEN!" in betstatus and betstatusid != 2:
				if alreadybet:
					newmonies = int(driver.find_element_by_xpath("//span[@id='balance']").text)
					moneychange = True
					print "Round over"
					print "--------------------------------------------------------"
					if monies < newmonies:
						print "You win!"
						correct[unknown] += 1
						total[unknown] += 1
						if lastbet == 'blue':
							lastwon = 'blue'
						else:
							lastwon = 'red'
					elif newmonies < monies:
						print "You lose!"
						total[unknown] += 1
						if lastbet == 'red':
							lastwon = 'blue'
						else:
							lastwon = 'red'
					else:
						moneychange = False
						print 'Bet did not go through'
					if moneychange:
						if lastwon == 'blue':
							newBlue = str(int(Rb + 32*(1-Eb)))
							del(f[bluePlayer])
							f[bluePlayer] = newBlue

							newRed = str(int(Rr + 32*(0-Er)))
							del(f[redPlayer])
							f[redPlayer] = newRed
							print bluePlayer+'['+newBlue+']', 'beats', redPlayer+'['+newRed+']'
						if lastwon == 'red':
							newBlue = str(int(Rb + 32*(0-Eb)))
							del(f[bluePlayer])
							f[bluePlayer] = newBlue

							newRed = str(int(Rr + 32*(1-Er)))
							del(f[redPlayer])
							f[redPlayer] = newRed
							print redPlayer+'['+newRed+']', 'beats', bluePlayer+'['+newBlue+']'
						monies = newmonies
						frec.write(str(monies)+"\n")
						print "Current monies: $" + str(monies)
				print ""
				unknown = 0
				newredPlayer = driver.find_element_by_xpath("//span[@id='p1name']").get_attribute("innerHTML")
				newbluePlayer = driver.find_element_by_xpath("//span[@id='p2name']").get_attribute("innerHTML")
				
				if f.get(newredPlayer) is None:
					f[newredPlayer] = 1400
					unknown += 1
				if f.get(newbluePlayer) is None:
					f[newbluePlayer] = 1400
					unknown += 1
				newRb = float(f[newbluePlayer].value)
				newRr = float(f[newredPlayer].value)

				newEr = 1.0/(1+10**((newRb-newRr)/400))
				newEb = 1.0/(1+10**((newRr-newRb)/400))

				print newredPlayer+'['+str(newRr)+']', 'vs', newbluePlayer+'['+str(newRb)+']'
				print "========================================================"
				print "Bets open"
				print "--------------------------------------------------------"
				betstatusid = 2
				wager = driver.find_element_by_xpath("//input[@id='wager']")
				wager.clear()
				driver.find_element_by_xpath("//body").click()
				wager.send_keys("1")
				body = driver.find_element_by_xpath("//body")
				body.click()
				if newEr > newEb:
					button = driver.find_element_by_xpath("//input[@name='player1']")
					button.click()
					currentbet = 'red'
					print '1 on', newredPlayer
				elif newEb > newEr:
					button = driver.find_element_by_xpath("//input[@name='player2']")
					button.click()
					currentbet = 'blue'
					print '1 on', newbluePlayer
				elif random.random() > 0.5:
					button = driver.find_element_by_xpath("//input[@name='player2']")
					button.click()
					currentbet = 'blue'
					print '1 on', newbluePlayer
				else:
					button = driver.find_element_by_xpath("//input[@name='player1']")
					button.click()
					currentbet = 'red'
					print '1 on', newredPlayer

				try:
					driver.find_element_by_xpath("//img[@src='../images/betload.gif']")
				except NoSuchElementException:
					print "could not bet, trying again"
					betstatusid = 0
				redPlayer = newredPlayer
				bluePlayer = newbluePlayer
				lastbet = currentbet
				Er = newEr
				Eb = newEb
				Rr = newRr
				Rb = newRb
				alreadybet = True
			time.sleep(5)
	except KeyboardInterrupt:
		f.close()
		frec.close()
		for i in range(0,3):
			facc.write(str(correct[i])+", "+str(total[i])+", ")
		facc.write("\n")
		facc.close()
		print "Finished"
		print str(correct[0]) + " of " + str(total[0]) + " correct when both known"
		print str(correct[1]) + " of " + str(total[1]) + " correct when one known"
		print str(correct[2]) + " of " + str(total[2]) + " correct when none known"
	except Exception, e:
		print e.__doc__
		print e.message
		f = open('log.txt','a')
		traceback.print_exc(f)
		f.close()
		traceback.print_exc(file=sys.stdout)
		print "Finished with errors"
		f.close()
		frec.close()
		for i in range(0,3):
			facc.write(str(correct[i])+", "+str(total[i])+", ")
		facc.write("\n")
		facc.close()
		pickle.dump(driver.get_cookies(), open("cookies.pkl","wb"))
		print str(correct[0]) + " of " + str(total[0]) + " correct when both known"
		print str(correct[1]) + " of " + str(total[1]) + " correct when one known"
		print str(correct[2]) + " of " + str(total[2]) + " correct when none known"
		time.sleep(120)
		import sort
		os.system("python main.py")

