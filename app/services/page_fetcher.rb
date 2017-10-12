require "open-uri"

class PageFetcher
  def initialize(post)
    @post = post
  end

  def content
    LinksRectifier.new(@post.link, raw_page_content)
      .content_with_rectified_links
  end

  private

  def raw_page_content
    open(@post.link).read
  end
end
