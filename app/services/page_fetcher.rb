require "open-uri"

class PageFetcher
  def initialize(post)
    @post_link = post.link
  end

  def content
    PageProxy.new(@post_link, raw_page_content).content.html_safe
  end

  private

  def raw_page_content
    open(@post_link).read
  end
end
