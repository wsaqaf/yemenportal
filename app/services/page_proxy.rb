class PageProxy
  MIME_TYPE_ATTRIBUTE = "type".freeze

  def initialize(page_url, page_content)
    @page_url = page_url
    @link_rectifier = PageProxy::LinkRectifier.new(@page_url)
    @content = Nokogiri::HTML(page_content)
  end

  def content
    add_base_tag
    rectify_page_links
    @content.inner_html
  end

  private

  def add_base_tag
    PageProxy::BaseTag.new(@content, @page_url).put_into_head
  end

  def rectify_page_links
    @content.search(*tags_with_url_attributes).each do |tag|
      tag_attributes(tag.name).each do |attr|
        if tag[attr].present?
          tag[attr] = @link_rectifier.rectify(tag[attr], tag.name, tag[MIME_TYPE_ATTRIBUTE])
        end
      end
    end
  end

  def config
    AttributesConfig.instance
  end

  delegate :tags_with_url_attributes, :tag_attributes, to: :config
end
