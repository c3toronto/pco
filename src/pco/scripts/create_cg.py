import os
from selenium import webdriver
from selenium.webdriver.common.by import By


def driver():
    driver = webdriver.Chrome()
    driver.set_window_size(500, 500)
    return driver

def logged_in_driver(driver):
    # Login steps
    driver.get("https://login.planningcenteronline.com/login/new")
    # print(driver.find_elements(By.ID, "email"), driver.find_elements(By.ID, "password"))
    driver.implicitly_wait(2)

    # don't re-login if already logged in
    if len(driver.find_elements(By.ID, "email")) > 0 and len(driver.find_elements(By.ID, "password")) > 0:
        driver.find_element(By.ID, "email").send_keys(os.environ("PCO_EMAIL")) 
        driver.find_element(By.ID, "password").send_keys(os.environ("PCO_PASSWORD"))
        driver.find_element(By.NAME, "commit").click()
        driver.find_element(By.CSS_SELECTOR, ".pane:nth-child(2) > .btn").click()
    
    return driver

def create_cg(logged_in_driver, group_name):
    driver = logged_in_driver
    
    driver.implicitly_wait(2)
    # 1 | open | /my_groups | 
    driver.get("https://groups.planningcenteronline.com/groups")
    driver.implicitly_wait(5)
    # 4 | click | xpath=//div[@id='filtered-groups-header']/div/div/div/button[2] | 
    driver.find_element(By.XPATH, "//div[@id=\'filtered-groups-header\']/div/div/div/button[2]").click()
    # 5 | click | id=group_group_type_id | 
    driver.find_element(By.ID, "group_group_type_id").click()
    # 6 | select | id=group_group_type_id | label=Connect Groups
    dropdown = driver.find_element(By.ID, "group_group_type_id")
    dropdown.find_element(By.XPATH, "//option[. = 'Connect Groups']").click()
    # 7 | click | id=group_name | 
    driver.find_element(By.ID, "group_name").click()
    # 8 | type | id=group_name | [TEST] Dev Selenium4
    driver.find_element(By.ID, "group_name").send_keys(str(group_name))

    driver.find_element(By.XPATH, "//span[contains(.,'Create group')]").click()
    driver.implicitly_wait(2)

    # add chat_enabled clicking here

    return driver

def get_group_id(pco, group_name):
    try:
        data = pco.get(f'/groups/v2/groups?where[name]={group_name}')
        print(f"Number of groups matching {group_name}: {len(data['data'])}")
        if data['data']:
            group_id = data['data'][0]['id']
            return group_id
        else:
            print(f"No group found with name: {group_name}")
            return
    except Exception as e:
        print(f"Error fetching group ID for {group_name}: {e}")
        return

def patch_group(pco, 
                group_id: int, 
                name: str = None,
                tags: int | list = None,
                schedule: str = None):
    attributes = {}
    if name:
        attributes['name'] = name
    if schedule:
        attributes['schedule'] = schedule
    if tags:
        attributes['tag_ids'] = tags

    response = pco.patch(f'/groups/v2/groups/{group_id}', payload={"data": {"attributes": attributes}})
    return response

def edit_group(driver):
    # enable chat
    # set location
    pass

def main():
    driver_init = driver()
    from pypco import PCO
    pco = PCO(app_id=os.environ["PCO_APP_ID"], api_key=os.environ["PCO_API_KEY"])
    

    import pandas as pd
    df = pd.read_csv("~/Downloads/Summer\ Connect\ Groups.csv")
    assert 'group_name' in df.columns, "group_name column not found in CSV"

    for _, row in df.iterrows():
        driver = logged_in_driver(driver_init)
        driver.implicitly_wait(2)

        group_name = row['group_name']
        driver = create_cg(driver, group_name)
        print(f"Created group: {group_name}")

        # enable chat and set location via Selenium
        driver = edit_group(driver)

        # add Tags (Season, Campus, Group Type, Regularity) and Schedule here
        patch_group(pco, 
                    group_id=get_group_id(pco, group_name), 
                    tags=row['tags'] if 'tags' in row else None,
                    schedule=row['schedule'] if 'schedule' in row else None,)
    
        


if __name__ == "__main__":
    main()