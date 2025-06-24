import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
from bs4 import BeautifulSoup
import requests
from pydantic import BaseModel, Field
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LLMConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import BM25ContentFilter
import re
import csv


async def main():


        
    raw_md_generator = DefaultMarkdownGenerator(
        content_source="raw_html",
        options={"ignore_links": True}
    )


    cleaned_md_generator = DefaultMarkdownGenerator(
        content_source="cleaned_html",  # This is the default
        options={"ignore_links": True}
    )


    fit_md_generator = DefaultMarkdownGenerator(
        content_source="fit_html",
        options={"ignore_links": True}
    )

    crawl_config = CrawlerRunConfig(
        markdown_generator=cleaned_md_generator,

    )

    browser_cfg = BrowserConfig(headless=True)

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        
        rows = []
        result = await crawler.arun(
            url="https://www.ibm.com/docs/en/mhs-and-em/7.6.2?topic=messages-bmxao0278e",
            config=crawl_config
        )

        if result.success:
           
            for link in result.links["internal"]:
                

                link = link['href']

                if "messages-bmxao" in link:
                    
                    result = await crawler.arun(
                        url = link,
                        config = crawl_config,
                    )

                    
                    match = re.search(
                            r'## Error submitting rating.*?(# BMXAO\d+E.*?)\nLast Updated: (.*?)\n+## Explanation\n(.*?)\n+## System action\n(.*?)\n+## User response\n(.*?)\n+## Administrator response\n(.*?)\n+\*\*Parent topic:',
                            result.markdown.raw_markdown,
                            re.DOTALL
                        )

                    if match:
                        code = match.group(1).strip()
                        last_updated = match.group(2).strip()
                        explanation = match.group(3).strip()
                        system_action = match.group(4).strip()
                        user_response = match.group(5).strip()
                        admin_response = match.group(6).strip()

                        # Format and print

                        rows.append({
                                "Code": code,
                                "Last Updated": last_updated,
                                "Explanation": explanation,
                                "System Action": system_action,
                                "User Response": user_response,
                                "Administrator Response": admin_response
                        })

                        # Save to CSV
                        if rows:
                            with open("ibm_error_reports.csv", mode="w", newline="", encoding="utf-8") as file:
                                writer = csv.DictWriter(file, fieldnames=rows[0].keys())
                                writer.writeheader()
                                writer.writerows(rows)

                            print(f"Saved {len(rows)} error sections to ibm_error_reports.csv")
                        else:
                            print("No error sections found.")
                    else:
                        print("Pattern not found. Check if the structure or headings changed.")
  
        else:
            print("Error:", result.error_message)

    # extraction_strategy = JsonCssExtractionStrategy(schema, verbose=True)

    # browser_config = BrowserConfig(verbose=True)

    # run_config = CrawlerRunConfig(
    #     # Content filtering
    #     word_count_threshold=10,
    #     #excluded_tags=['form', 'header','footer','nav'],
    #     exclude_external_links=True,
    #     extraction_strategy=extraction_strategy,
    #     # Content processing
    #     process_iframes=True,
    #     remove_overlay_elements=True,
        

    #     # Cache control
    #     cache_mode=CacheMode.ENABLED  # Use cache if available
    # )

    # async with AsyncWebCrawler(config=browser_config) as crawler:
    #     result = await crawler.arun(
    #         url="https://www.ibm.com/docs/en/mhs-and-em/7.6.2?topic=messages-bmxao0278e",
    #         config=run_config
    #     )

    #     if result.success:
    #         # Print clean content
    #         # print("Content:", result.markdown.raw_markdown)  # First 500 chars

    #         # # Process images
    #         # for image in result.media["images"]:
    #         #     print(f"Found image: {image['src']}")

    #         # # Process links
    #         for link in result.links["internal"]:
    #             #print(f"Internal link: {link['href']}")

    #             link = link['href']

    #             if "messages-bmxao" in link:
                    
    #                 result = await crawler.arun(
    #                     url = link,
    #                     config = run_config,

    #                 )

    #                 print(result)
    #                 # data = json.loads(result.extracted_content)

    #                 # print(data)
    #                 # print(json.dumps(data[0], indent=2) if data else "No data found")

    #                 print("############")
    #                 print("############")
    #                 if not result.success:
    #                     print("Crawl failed:", result.error_message)
    #                     return

    #                 # 5. Parse the extracted JSON


    #                 print(result)
    #                 break
                    
    #     else:
    #         print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(main())
