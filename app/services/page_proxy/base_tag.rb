class PageProxy::BaseTag
  BASE_TAG_NAME = "base".freeze
  LINK_REFERENCE_ATTRIBUTE = "href".freeze
  LINK_TARGET_ATTRIBUTE = "target".freeze
  NEW_TAB_TARGET = "_blank".freeze

  def initialize(html_content, base_url)
    @html_content = html_content
    @base_tag = Nokogiri::XML::Node.new(BASE_TAG_NAME, @html_content)
    @base_tag[LINK_TARGET_ATTRIBUTE] = NEW_TAB_TARGET
    @base_tag[LINK_REFERENCE_ATTRIBUTE] = base_url
  end

  def put_into_head
    @html_content.search(:head).first.add_child(@base_tag)
  end
end
