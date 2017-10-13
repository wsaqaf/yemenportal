class PageProxy::AttributesConfig
  CONFIG_FILE_NAME = "html_attributes_with_links.yml".freeze
  CONFIG_DIRECTORY = "config".freeze

  def initialize
    @attributes_with_url = load_config
  end

  def self.instance
    @instance ||= PageProxy::AttributesConfig.new
  end

  def tags_with_url_attributes
    @attributes_with_url.keys
  end

  def tag_attributes(tag)
    Array(@attributes_with_url[tag])
  end

  private

  def load_config
    YAML.load_file(Rails.root.join(CONFIG_DIRECTORY, CONFIG_FILE_NAME))
  end
end
